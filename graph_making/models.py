from django.db import models


# Create your models here.
class WordData(models.Model):
    VID = models.CharField(max_length=100)
    Company_ID = models.CharField(max_length=100)
    Survey_ID = models.IntegerField()
    Cust_ID = models.IntegerField()
    question = models.IntegerField()
    start = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    end = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    conf = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    content = models.CharField(max_length=100)
    pron = models.CharField(max_length=100)
    mean_time = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    der_score = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    MF = models.IntegerField()
    net_score = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    sec = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    Sentiment = models.CharField(max_length=100)
    SCORE = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)


class TranscriptData(models.Model):
    VID_ID = models.CharField(max_length=100)
    Company_ID = models.CharField(max_length=100)
    Survey_ID = models.IntegerField()
    Cust_ID = models.IntegerField()
    question = models.IntegerField()
    transcript = models.CharField(max_length=100)
    SpeakTime = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    num_words = models.IntegerField()
    Hurriness = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    Score = models.DecimalField(max_digits=20, decimal_places=4, default=0.0)
    AverageConfidence = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)


class AggregateData(models.Model):
    Question = models.IntegerField()
    Positive_count = models.IntegerField()
    Negative_count = models.IntegerField()
    Neutral_count = models.IntegerField()
    Pos_Neg_words = models.IntegerField()
    Total_words = models.IntegerField()
    Positive_percent = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    Negative_percent = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    Neutral_percent = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    Pos_percent = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)
    Neg_percent = models.DecimalField(max_digits=20, decimal_places=10, default=0.0)


class SentimentAggregateTable(models.Model):
    Question = models.IntegerField()
    number_of_positive_sentence = models.IntegerField()
    number_of_negative_sentence = models.IntegerField()
    number_of_neutral_sentence = models.IntegerField()
