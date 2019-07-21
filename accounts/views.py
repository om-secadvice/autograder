from django.shortcuts import render,redirect
from django.contrib.auth import views
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DefaultLoginView
# Create your views here.

@login_required
def PasswordChangeDone(request):
    message=['Password Changed Successfully']
    request.session['messages']=message
    return redirect('dashboard')




class LoginView(DefaultLoginView):
    redirect_authenticated_user = True

