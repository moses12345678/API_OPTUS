# serializers.py
from rest_framework.serializers import Serializer, URLField, IntegerField

class BenchmarkSerializer(Serializer):
    url = URLField()
    requests = IntegerField(min_value=1, default=1000)
    concurrency = IntegerField(min_value=1, default=100)
