from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Serializer, URLField, IntegerField
from .serializers import *
import subprocess


class BenchmarkAPIView(APIView):
    def post(self, request):
        serializer = BenchmarkSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            requests = serializer.validated_data['requests']
            concurrency = serializer.validated_data['concurrency']

            # Run `ab` inside the Docker container
            try:
                command = [
                    "ab",
                    f"-n {requests}",
                    f"-c {concurrency}",
                    url
                ]
                result = subprocess.run(command, capture_output=True, text=True, check=True)

                # Parse the results
                raw_output = result.stdout
                lines = raw_output.split("\n")
                rps, time_per_request, total_transferred = None, None, None

                for line in lines:
                    if "Requests per second" in line:
                        rps = float(line.split(":")[1].strip().split(" ")[0])
                    if "Time per request" in line and "(mean)" in line:
                        time_per_request = float(line.split(":")[1].strip().split(" ")[0])
                    if "Total transferred" in line:
                        total_transferred = line.split(":")[1].strip()

                # Generate recommendations
                recommendations = []
                if rps < 50:
                    recommendations.append("Optimize server or add scaling.")
                if time_per_request > 500:
                    recommendations.append("Reduce response time via caching or database optimization.")
                if not recommendations:
                    recommendations.append("API is performing well!")

                return Response({
                    "requests_per_second": f"{rps:.2f} [#/sec]",
                    "time_per_request": f"{time_per_request:.2f} [ms]",
                    "total_transferred": total_transferred,
                    "recommendations": recommendations,
                    "raw_output": raw_output,
                }, status=status.HTTP_200_OK)

            except subprocess.CalledProcessError as e:
                return Response({"error": f"Benchmarking failed: {e.stderr}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

