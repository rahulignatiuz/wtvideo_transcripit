"""video_transcript URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, path
from .views import VideoDownloads, sendMail, register_request, register_success, login_request, logout_request, \
    login_success, AWSTranscribe

urlpatterns = [
    path('', sendMail),
    path('api/', VideoDownloads.as_view()),
    path('aws/', AWSTranscribe.as_view()),
    path("register/", register_request, name="register"),
    path("r_success/", register_success, name="r_success"),
    path("l_success/", login_success, name="l_success"),
    path("login/", login_request, name="login"),
    path('accounts/', include('allauth.urls')),
    path("logout/", logout_request, name="logout")
]
