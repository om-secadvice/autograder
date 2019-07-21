from django import forms
from .models import StudentAssignment,Assignment
from django.forms import ValidationError
import magic
from autograder import settings
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _

def extensions(file_type):
    map={'python':'.py,.pyw','zip':'.zip','image':'image/*','text':'text/*'}
    return map[file_type]

class StudentAssignmentForm(forms.ModelForm):
    assignment = forms.ModelChoiceField(queryset=Assignment.objects.all(),
            widget=forms.HiddenInput())
    solution_file= forms.FileField(allow_empty_file=False,widget=forms.ClearableFileInput(attrs={'hidden':True}),required=True,max_length=100)
    need_late_days = forms.BooleanField(required=False)
    class Meta:
        model = StudentAssignment
        fields = ('assignment','solution_file', )

    def __init__(self, *args, **kwargs):
        
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        #  create a user attribute and take it out from kwargs
        # so it doesn't messes up with the other formset kwargs
        assignment=self.get_initial_for_field(self.fields['assignment'],'assignment')

        if assignment is not None:
            self.fields['solution_file'].widget.attrs.update({'id':'solution_file_'+str(assignment.id),'accept':extensions(assignment.solution_file_type)})
            

            
    def clean_solution_file(self):
        data = self.cleaned_data["solution_file"]
        assignment=self.cleaned_data["assignment"]
        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)
        if data.size > int(settings.MAX_UPLOAD_SIZE):
            params={'File Size':data.size}
            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s' % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(data.size))),params=params)
        
        if  content_type.find(assignment.solution_file_type) == -1:
            params={'content-type':assignment.solution_file_type}
            raise ValidationError("Content type mismatch. Expected %s"%(assignment.solution_file_type),params=params)
        
        return data
    
   


    
