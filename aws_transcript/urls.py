from django.urls import include, path
from .views import AWSTranscribe, UploadLexiconDataView

urlpatterns = [
    path('aws/transcribe', AWSTranscribe.as_view()),
    path('upload', UploadLexiconDataView.as_view(), name='upload-file')
]
