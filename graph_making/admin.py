from django.contrib import admin

# Register your models here.
from graph_making.models import WordData, TranscriptData, AggregateData, SentimentAggregateTable


class WordDataAdmin(admin.ModelAdmin):
    list_display = (
        'VID', 'Company_ID', 'Survey_ID', 'Cust_ID', 'question', 'start', 'end', 'conf', 'content',
        'pron', 'mean_time', 'der_score', 'MF', 'net_score', 'sec', 'Sentiment', 'SCORE')


class TranscriptDataAdmin(admin.ModelAdmin):
    list_display = (
        'VID_ID', 'Company_ID', 'Survey_ID', 'Cust_ID', 'question', 'transcript', 'SpeakTime', 'num_words', 'Hurriness',
        'Score', 'AverageConfidence')


class AggregateDataAdmin(admin.ModelAdmin):
    list_display = (
        'Question', 'Positive_count', 'Negative_count', 'Neutral_count', 'Pos_Neg_words', 'Total_words',
        'Positive_percent', 'Negative_percent', 'Neutral_percent',
        'Pos_percent', 'Neg_percent')


class SentimentAggregateTableAdmin(admin.ModelAdmin):
    list_display = (
    'Question', 'number_of_positive_sentence', 'number_of_negative_sentence', 'number_of_neutral_sentence')


admin.site.register(WordData, WordDataAdmin)
admin.site.register(TranscriptData, TranscriptDataAdmin)
admin.site.register(AggregateData, AggregateDataAdmin)
admin.site.register(SentimentAggregateTable, SentimentAggregateTableAdmin)
