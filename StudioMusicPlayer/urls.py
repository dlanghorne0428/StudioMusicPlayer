"""StudioMusicPlayer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.urls import static

from App.views import user_access

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("App.urls")),   
    
    # this include of accounts adds several common URL patterns
    # see "Authentication Views section of https://docs.djangoproject.com/en/4.0/topics/auth/default/
    path('accounts/', include('django.contrib.auth.urls')),
    
    # add patterns for user signup / creation 
    path('accounts/signup/', user_access.SignUpView.as_view(), name='signup'),
    path('accounts/signup/teacher/', user_access.TeacherSignUpView.as_view(), name='teacher_signup')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)