from django.urls import path,include
from autograder.settings import PROTECTED_MEDIA_AS_DOWNLOADS,PROTECTED_MEDIA_SERVER
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('late_days/',views.latedays,name='latedays'),
    path('protected/<str:filepath>/<str:filename>',views.protected_media,{
            "server": PROTECTED_MEDIA_SERVER,
            "as_download": PROTECTED_MEDIA_AS_DOWNLOADS
        },name='submitted'),
]
