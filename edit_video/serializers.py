from rest_framework import serializers

from aws_transcript.models import Word, Transcript, LexiconData


class WordEditSerializer(serializers.ModelSerializer):
    # transcript_id = TranscriptSerializer()

    class Meta:
        model = Word
        # fields = ("id", 'transcript_id', 'start_time', 'end_time', 'content', 'pron', 'confidence')
        fields = '__all__'


class TranscriptEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transcript
        fields = '__all__'