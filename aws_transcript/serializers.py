from rest_framework import serializers

from aws_transcript.models import Word, Transcript, LexiconData


class WordSerializer(serializers.ModelSerializer):
    # transcript_id = TranscriptSerializer()

    class Meta:
        model = Word
        # fields = ("id", 'transcript_id', 'start_time', 'end_time', 'content', 'pron', 'confidence')
        fields = '__all__'


class TranscriptSerializer(serializers.ModelSerializer):
    word_details = WordSerializer(many=True)

    class Meta:
        model = Transcript
        # fields = '__all__'
        fields = (
            "id", 'response_id', 'transcript', 'video_name', 'word_details', 'average_confidence', 'total_words',
            'score',
            'average_score',
            'score_sd', 'question')


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class SaveFileSerializer(serializers.Serializer):
    class Meta:
        model = LexiconData
        fields = "__all__"
