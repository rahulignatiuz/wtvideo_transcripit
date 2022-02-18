from django.contrib import admin
from aws_transcript.models import Transcript, Word, LexiconData


# Register your models here.


class TranscriptAdmin(admin.ModelAdmin):
    list_display = (
    'response_id', 'transcript', 'video_name', 'average_confidence', 'total_words', 'score', 'average_score',
    'score_sd', 'score_per_statement')


class WordAdmin(admin.ModelAdmin):
    list_display = (
    'transcript_id', 'start_time', 'end_time', 'content', 'pron', 'confidence', 'mean_time', 'der_score', 'mf',
    'net_score', 'second', 'sentiment', 'score')


class LexiconDataAdmin(admin.ModelAdmin):
    list_display = ('content', 'sentiment', 'score')


admin.site.register(Transcript, TranscriptAdmin)
admin.site.register(Word, WordAdmin)
admin.site.register(LexiconData, LexiconDataAdmin)
