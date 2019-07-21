from django.db import models
from accounts.models import User
from django.utils.translation import ugettext_lazy as _
import os
from autograder.settings import BASE_DIR
import datetime


from django.core.files.storage import FileSystemStorage
from autograder.settings import PROTECTED_MEDIA_ROOT, PROTECTED_MEDIA_URL


class ProtectedFileSystemStorage(FileSystemStorage):
    """
    A class to manage protected files.
    We have to override the methods in the FileSystemStorage class which
    are decorated with cached_property for this class to work as intended.
    """
    def __init__(self, *args, **kwargs):
        kwargs["location"] = PROTECTED_MEDIA_ROOT
        kwargs["base_url"] = PROTECTED_MEDIA_URL
        super(ProtectedFileSystemStorage, self).__init__(*args, **kwargs)


class ProtectedFileField(models.FileField):
    def __init__(self,*args, **kwargs):
        kwargs["storage"] = ProtectedFileSystemStorage()
        super(ProtectedFileField, self).__init__(*args,**kwargs)


class Assignment(models.Model):
    name = models.CharField(_('name'),max_length=100)
    number = models.IntegerField(_('number'))
    part = models.IntegerField(_('part'))
    deadline = models.DateTimeField(_('deadline'))
    file = models.FileField(_('file'),upload_to="assignment/")
    solution_file_type = models.CharField(_('solution_file_type'),max_length=100)
    class Meta:
        unique_together = (('number', 'part'),)
    
def filenamer(instance,filename):
    return os.path.join('submissions','solution_{}_{}_{}.{}'.format(instance.assignment.number,instance.assignment.part,instance.user.roll_number,filename.split('.')[-1]))
# Create your models here.
class StudentAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='student')
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='assignment')
    submitted_on = models.DateTimeField(_('submitted_on'),blank=True)
    submission_count = models.IntegerField(_('submission_count'),blank=True, default=0)
    penalty = models.FloatField(_('penalty'),default=0,blank=True)
    solution_file = ProtectedFileField(_('solution_file'),upload_to=filenamer)
    need_late_days = models.BooleanField(_('need_late_days'), default=False)
    late_days_used = models.DurationField(_('late_days_count'),default=datetime.timedelta(days=0))
    
    class Meta:
        unique_together = (('user', 'assignment', 'submitted_on'),)

