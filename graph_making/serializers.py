from rest_framework import serializers

from graph_making.models import AggregateData, SentimentAggregateTable


class AggregateDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregateData
        fields = '__all__'


class SentimentAggregateTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAggregateTable
        fields = '__all__'
