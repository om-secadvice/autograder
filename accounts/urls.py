from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view() , name='logout'),
    path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
]
