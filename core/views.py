from django.shortcuts import render,redirect
from django.http.response import HttpResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import StudentAssignmentForm
from .models import Assignment,StudentAssignment
from django.utils import timezone
from django.template.defaultfilters import time_format
from .templatetags.app_filters import smooth_timedelta
import datetime,os
from django.db import transaction
from django.core.exceptions import PermissionDenied 
from autograder.settings import MEDIA_ROOT
from django.views.static import serve
from os.path import basename
import mimetypes
from autograder.settings import PROTECTED_MEDIA_LOCATION_PREFIX, PROTECTED_MEDIA_ROOT,MEDIA_URL
# Create your views here.

mimetypes.add_type('text/plain','.output')

def reportlink(student_assignment):
    name=student_assignment.solution_file.file.name
    if student_assignment.assignment.solution_file_type == "python":
        filename=name.split('/')[-1]
        filepath="submissions/"+filename.split('.')[0]+'.output'
    else:
        filepath="#"
    return filepath


def ceildays(d):
    if d.seconds%(24*60*60)==0:
        return datetime.timedelta(days=d.days)
    return datetime.timedelta(days=d.days+1)

@login_required
def dashboard(request):
    """GET: If user is not authenticated redirect to login page else serve dashboard.html
       POST: If user is not authenticated redirect to login else process submission of assignment"""
    first_time=request.session.get('first_time',False)
      
    timezone.activate(timezone.get_default_timezone())
    user=request.user
    messages=request.session.get('messages',[])
    if not first_time:
        request.session['first_time']=True
        messages=['Hi {}!'.format(user.name)]
        messages.append('Last Login: {}'.format(timezone.template_localtime(user.last_login)))

    
  
    if request.method == 'POST':
        form=StudentAssignmentForm(request.POST,request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    now = timezone.now()    
                    student_assignment=form.save(commit=False)
                    prev_submission = StudentAssignment.objects.filter(user=user, assignment=student_assignment.assignment).order_by('-submitted_on')
                    if request.POST.get('need_late_days',"off")=="on":
                        print("here")
                        student_assignment.need_late_days=True
                    if student_assignment.assignment.deadline+datetime.timedelta(hours=3)>now:
                        messages.append('Yay! You submitted within grace period')
                        pass
                    elif student_assignment.need_late_days:    
                        if user.late_days>=ceildays(now - student_assignment.assignment.deadline):
                            diff =ceildays(now-student_assignment.assignment.deadline)
                            if prev_submission is not None:
                                if prev_submission[0].late_days_used:
                                    diff = ceildays(diff-prev_submission[0].late_days_used)
                                
                            user.late_days=ceildays(user.late_days-diff)
                            student_assignment.late_days_used = ceildays(now-student_assignment.assignment.deadline)
                            
                        # elif user.late_days>datetime.timedelta(days=0):
                        else:
                            pen_days = ceildays(now - student_assignment.assignment.deadline - user.late_days)
                            student_assignment.penalty=(pen_days.days) * 30
                            student_assignment.late_days_used = user.late_days
                            user.late_days=datetime.timedelta(days=0)
                        user.save()
                    else:
                        pen_days = ceildays(now - student_assignment.assignment.deadline)
                        student_assignment.penalty=(pen_days.days)* 30
                    student_assignment.user=user
                    student_assignment.submitted_on=now
                    try:
                        student_assignment.submission_count+=1+prev_submission[0].submission_count
                        print(prev_submission[0].submission_count)
                    except:
                        student_assignment.submission_count+=1
                        
                    student_assignment.save()
                    messages=['Assignment submitted.','You can submit as many times as you want but only the last submission will be graded.']
            except PermissionError:
                messages['Assignment can\'t be submitted.']
        else:
           messages=[form.errors[i] for i in form.errors]
    
    #Create form list for active assignements
    assignments = Assignment.objects.all()

    active_assignments=assignments.filter(deadline__gte=timezone.now())
   
    late_assignments=assignments.filter(deadline__gte=timezone.now()-datetime.timedelta(days=3,hours=3),deadline__lt=timezone.now())
    late_forms=[ (StudentAssignmentForm(initial={'assignment':assignment}),assignment,assignment.deadline+datetime.timedelta(days=3,hours=3),True) for assignment in late_assignments]

    active_forms=[ (StudentAssignmentForm(initial={'assignment':assignment}),assignment,None,False) for assignment in active_assignments]


    #Create list of all submitted assignments
    student_assignments=StudentAssignment.objects.filter(user=user).order_by('-assignment')
    # print([student_assignment.id for student_assignment in student_assignments])
    context={'username':request.user.name,'forms':[active_forms,late_forms],'student_assignments':[(student_assignment,reportlink(student_assignment)) for student_assignment in student_assignments],'messages':messages}
    try:
        del request.session['messages']
    except:
        pass
    return render(request, 'dashboard.html',{'context':context})




@login_required
def latedays(request):
    return HttpResponse("You currently have extra "+smooth_timedelta(request.user.late_days))






@login_required
def protected_media(request, filepath,filename, server="nginx", as_download=False):
    path=filepath+'/'+filename
    print(path)
    
    access_granted=request.user.is_superuser
    
    
    if path.find(request.user.roll_number) > -1:
        access_granted=True
        
    if access_granted:
        
        if server != "django":
            mimetype, encoding = mimetypes.guess_type(path)
            response = HttpResponse()
            
            if mimetype:
                response["Content-Type"] = mimetype
            else:
                del response["Content-Type"]

            if encoding:
                response["Content-Encoding"] = encoding

            if as_download:
                response["Content-Disposition"] = "attachment; filename={}".format(
                    basename(path))
            
            response['X-Accel-Redirect'] = os.path.join(
                PROTECTED_MEDIA_LOCATION_PREFIX, path
            )
            print(response['X-Accel-Redirect'],response['Content-Type'])

            
        else:
            response = serve(
                request, path, document_root=PROTECTED_MEDIA_ROOT,
                show_indexes=False
            )

        return response
    else:
        return HttpResponseForbidden("You are not authorized.")
