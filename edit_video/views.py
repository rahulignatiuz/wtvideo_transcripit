import json
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from aws_transcript.models import Word, Transcript
from edit_video.helper import get_edit_video, aggregate_data_transcript, aggregate_data_word, convert_webm_to_mp4
from edit_video.serializers import TranscriptEditSerializer, WordEditSerializer


class VideoEditing(APIView):
    def post(self, request, format=None):
        net_score = request.data['net_score']
        result_status, result = get_edit_video(net_score)
        print(result_status, "++++++++++++result_status+++++++++++", result)
        if result_status:
            content = {
                "status": "success",
                "blob_video_url": result
            }
            return Response(content, status=status.HTTP_201_CREATED)
        else:
            content = {
                "status": "failure",
                "reason": result
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)


class AggregateDataWord(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        word_data = Word.objects.all()
        wr_serializer = WordEditSerializer(word_data, many=True)
        df_word = pd.json_normalize(wr_serializer.data)
        js = aggregate_data_word(df_word)
        print(js)
        content = {
            "status": "success",
            "result": json.loads(js)
        }
        return Response(content, status.HTTP_201_CREATED)


class AggregateDataTranscript(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        transcript_data = Transcript.objects.all()
        tr_serializer = TranscriptEditSerializer(transcript_data, many=True)
        df_tran = pd.json_normalize(tr_serializer.data)
        js = aggregate_data_transcript(df_tran)
        content = {
            "status": "success",
            "result": json.loads(js)
        }
        return Response(content, status.HTTP_201_CREATED)


class WordCloud(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        word_data = Word.objects.all()
        wr_serializer = WordEditSerializer(word_data, many=True)
        df_word = pd.json_normalize(wr_serializer.data)
        word_cloud_positive_Q1_Df = pd.DataFrame()
        word_cloud_positive_Q2_Df = pd.DataFrame()
        word_cloud_positive_Q3_Df = pd.DataFrame()
        word_cloud_negative_Q1_Df = pd.DataFrame()
        word_cloud_negative_Q2_Df = pd.DataFrame()
        word_cloud_negative_Q3_Df = pd.DataFrame()

        word_cloud_positive_Q1 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 1)]
        word_cloud_positive_Q1_list = word_cloud_positive_Q1['content'].unique()
        # word_cloud_positive_Q1_Df = pd.DataFrame(word_cloud_positive_Q1_list)

        word_cloud_positive_Q2 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 2)]
        word_cloud_positive_Q2_list = word_cloud_positive_Q2['content'].unique()
        # word_cloud_positive_Q2_Df = pd.DataFrame(word_cloud_positive_Q2_list)

        word_cloud_positive_Q3 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 3)]
        word_cloud_positive_Q3_list = word_cloud_positive_Q3['content'].unique()
        # word_cloud_positive_Q3_Df = pd.DataFrame(word_cloud_positive_Q3_list)

        word_cloud_negative_Q1 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 1)]
        word_cloud_negative_Q1_list = word_cloud_negative_Q1['content'].unique()
        # word_cloud_negative_Q1_Df = pd.DataFrame(word_cloud_negative_Q1_list)

        word_cloud_negative_Q2 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 2)]
        word_cloud_negative_Q2_list = word_cloud_negative_Q2['content'].unique()
        # word_cloud_negative_Q2_Df = pd.DataFrame(word_cloud_negative_Q2_list)

        word_cloud_negative_Q3 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 3)]
        word_cloud_negative_Q3_list = word_cloud_negative_Q3['content'].unique()
        # word_cloud_negative_Q3_Df = pd.DataFrame(word_cloud_negative_Q3_list)

        content = {
            "status": "success",
            "word_cloud_positive_Q1_list": word_cloud_positive_Q1_list,
            "word_cloud_positive_Q2_list": word_cloud_positive_Q2_list,
            "word_cloud_positive_Q3_list ": word_cloud_positive_Q3_list,
            "word_cloud_negative_Q1_list": word_cloud_negative_Q1_list,
            "word_cloud_negative_Q2_list ": word_cloud_negative_Q2_list,
            "word_cloud_negative_Q3_list": word_cloud_negative_Q3_list
        }
        return Response(content, status.HTTP_201_CREATED)


class CovertMP4(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        video_url = request.data['video_url']
        blob_video_url = convert_webm_to_mp4(video_url)
        if blob_video_url:
            content = {
                "status": "success",
                "blob_video_url": blob_video_url
            }
            return Response(content, status.HTTP_201_CREATED)
        else:
            content = {
                "status": "failure"
            }
            return Response(content, status.HTTP_404_NOT_FOUND)
