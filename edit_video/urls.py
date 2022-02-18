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
from .views import VideoEditing, AggregateDataWord, AggregateDataTranscript, WordCloud, CovertMP4

urlpatterns = [
    path("edit", VideoEditing.as_view(), name="edit"),
    path('aggregate/word', AggregateDataWord.as_view(), name='aggregate_word'),
    path('aggregate/transcript', AggregateDataTranscript.as_view(), name='aggregate_transcript'),
    path('word/cloud', WordCloud.as_view(), name='word_cloud'),
    path('covert/mp4', CovertMP4.as_view(), name='covert_mp4')

]
