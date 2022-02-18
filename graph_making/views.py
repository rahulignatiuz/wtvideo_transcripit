from rest_framework import status
from rest_framework.response import Response
from graph_making.models import AggregateData, SentimentAggregateTable
from rest_framework import generics
from graph_making.serializers import AggregateDataSerializer, SentimentAggregateTableSerializer


class AggregateDataAPI(generics.ListCreateAPIView):
    def get(self, request):
        aggregate_data = AggregateData.objects.all()
        serializer = AggregateDataSerializer(aggregate_data, many=True)
        content = {
            "status": "success",
            "aggregate_data": serializer.data
        }
        return Response(content, status=status.HTTP_201_CREATED)


class SentimentAggregateTableAPI(generics.ListCreateAPIView):
    def get(self, request):
        aggregate_data = SentimentAggregateTable.objects.all()
        serializer = SentimentAggregateTableSerializer(aggregate_data, many=True)
        content = {
            "status": "success",
            "aggregate_data": serializer.data
        }
        return Response(content, status=status.HTTP_201_CREATED)
