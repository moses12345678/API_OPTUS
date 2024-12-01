from django.urls import path, include
from .views import *

urlpatterns = [
    path("run/", BenchmarkAPIView.as_view(), name="benchmark_api"),
]