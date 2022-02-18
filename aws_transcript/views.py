import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from aws_transcript.helper import aws_transcribe
from aws_transcript.models import Transcript, LexiconData, Word
from aws_transcript.serializers import TranscriptSerializer, FileUploadSerializer, WordSerializer


class AWSTranscribe(APIView):
    def post(self, request, format=None):
        urls = request.data['url']
        transcribe_id, success_status = aws_transcribe(urls)


        # if success_status == "Success":
        #     transcript_data = Transcript.objects.filter(pk__in=transcribe_id)
        #     serializer = TranscriptSerializer(transcript_data, many=True)
        #     result = serializer.data
        # else:
        #     result = "Some Error...."

        content = {
            "result": transcribe_id
        }
        return Response(transcribe_id, status=status.HTTP_201_CREATED)


class UploadLexiconDataView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _, row in reader.iterrows():
            new_file = LexiconData(
                content=row['content'],
                sentiment=row['Sentiment'],
                score=row['SCORE']
            )
            new_file.save()
        return Response({"status": "success"}, status.HTTP_201_CREATED)