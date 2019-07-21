from __future__ import unicode_literals
from django.utils import timezone

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
import datetime
from .managers import UserManager
timezone.activate(timezone.get_current_timezone())
class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(_('email address'), primary_key=True)
    name = models.CharField(_('name'), max_length=30)
    date_joined = models.DateTimeField(_('date joined'),default=timezone.now)
    is_active = models.BooleanField(_('status'), default=True)
    late_days = models.DurationField(_('late_days'),default=datetime.timedelta(days=7))
    roll_number = models.CharField(_('roll_number'),max_length=8,unique=True)
    is_staff = models.BooleanField(_('staff'),default=False)
    is_superuser = models.BooleanField(_('superuser'),default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','roll_number']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the name.
        '''
        full_name = '%s' % (self.name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the name.
        '''
        full_name = '%s' % (self.name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)
    

