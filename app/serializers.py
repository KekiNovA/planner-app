from rest_framework import serializers
from datetime import datetime


class PlannerSerializer(serializers.Serializer):
    location = serializers.CharField(required=True)
    start_time = serializers.CharField(required=True)
    end_time = serializers.CharField(required=True)

    def validate(self, data):
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        try:
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise serializers.ValidationError(
                "Incorrect date format, should be YYYY-MM-DD HH:MM:SS")

        if start_time >= end_time:
            raise serializers.ValidationError(
                "Start time must be less than end time")

        return data
