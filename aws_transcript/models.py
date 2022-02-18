from django.db import models


# Create your models here.

class Transcript(models.Model):
    response_id = models.CharField(max_length=50)
    transcript = models.TextField()
    video_name = models.URLField(max_length=200)
    question = models.IntegerField(default=0)
    average_confidence = models.DecimalField(max_digits=30, decimal_places=5, null=True, blank=True)
    total_words = models.IntegerField(default=0)
    score = models.DecimalField(max_digits=30, decimal_places=3, null=True, blank=True)
    average_score = models.DecimalField(max_digits=30, decimal_places=3, null=True, blank=True)
    score_sd = models.DecimalField(max_digits=30, decimal_places=3, null=True, blank=True)
    score_per_statement = models.DecimalField(max_digits=30, decimal_places=3, default=0.00, null=True, blank=True)

    def __str__(self):
        return str(self.response_id)


class Word(models.Model):
    start_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    content = models.CharField(max_length=30, null=True, blank=True)
    pron = models.CharField(max_length=30, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    mean_time = models.DecimalField(max_digits=30, decimal_places=5, null=True, blank=True)
    der_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, null=True, blank=True)
    mf = models.IntegerField(default=0)
    net_score = models.DecimalField(max_digits=10, decimal_places=3, default=0.00, null=True, blank=True)
    second = models.IntegerField(default=0)
    sentiment = models.CharField(max_length=30, default='NEU', null=True)
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, null=True, blank=True)
    transcript_id = models.ForeignKey(Transcript, related_name="word_details", on_delete=models.CASCADE)
    question = models.IntegerField(default=0)


class LexiconData(models.Model):
    content = models.CharField(max_length=30, null=True)
    sentiment = models.CharField(max_length=30, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
