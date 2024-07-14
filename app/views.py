import requests
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import PlannerSerializer
from django.conf import settings


def get_lat_long(location):
    """
    Retrieve latitude and longitude for a given location.

    Args:
        location (str): Name of the location to get coordinates for.

    Returns:
        tuple: Latitude and longitude of the location.
    """
    api_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        'name': location,
        'count': 1
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    return data['results'][0]['latitude'], data['results'][0]['longitude']


def get_weather_forcast(latitude, longitude, start_time, end_time):
    """
    Get weather forecast for the specified coordinates and time range.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start_time (str): Start time for the forecast in 'YYYY-MM-DD HH:MM:SS' format.
        end_time (str): End time for the forecast in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
        list: A list of dictionaries containing time and weather conditions.
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light intensity",
        53: "Drizzle: Moderate intensity",
        55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light intensity",
        57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight intensity",
        63: "Rain: Moderate intensity",
        65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light intensity",
        67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight intensity",
        73: "Snow fall: Moderate intensity",
        75: "Snow fall: Heavy intensity",
        77: "Snow grains",
        80: "Rain showers: Slight intensity",
        81: "Rain showers: Moderate intensity",
        82: "Rain showers: Violent intensity",
        85: "Snow showers: Slight intensity",
        86: "Snow showers: Heavy intensity",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'timezone': 'IST',
        'start_hour': datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').isoformat(timespec='minutes'),
        'end_hour': datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S').isoformat(timespec='minutes'),
        'hourly': 'weather_code'
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    forecast = []
    for count in range(len(data['hourly']['weather_code'])):
        forecast.append({'time': data['hourly']['time'][count],
                        'weather_condition': weather_codes.get(data['hourly']['weather_code'][count], "Unknown code")})
    return forecast


def get_nearby_places(latitude, longitude):
    """
    Retrieve nearby tourist attractions for the specified coordinates.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        list: A list of names of nearby tourist attractions.
    """
    api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f'{latitude},{longitude}',
        'radius': 1500,
        'type': 'tourist_attraction',
        'key': settings.GOOGLE_API_KEY
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    places = [place['name'] for place in data['results']]
    return places


class PlannerAPIView(APIView):
    """
    API view to handle POST requests for getting weather forecast and nearby tourist attractions.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this view.

    Methods:
        - post: Handles POST requests, validates the request data, retrieves weather forecast and nearby places,
                and returns them in the response.
    """
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(request_body=PlannerSerializer,
                         responses={201: '''When forecast and point of interests are able to fetch. return weather_forecast and point_of_interest''',
                                    400: '''Gives Validation Error''',
                                    401: '''Gives invalid data error''',
                                    500: '''Internal Server Error'''}
                         )
    def post(self, request):
        serializer = PlannerSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            location = serializer.validated_data['location']
            latitude, longitude = get_lat_long(location=location)
            forecast = get_weather_forcast(latitude=latitude, longitude=longitude,
                                           start_time=serializer.validated_data['start_time'], end_time=serializer.validated_data['end_time'])
            places = get_nearby_places(latitude=latitude, longitude=longitude)
            return Response({'weather_forecast': forecast, 'point_of_interest': places}, status=status.HTTP_200_OK)

        except (ValidationError, serializers.ValidationError) as e:
            return Response({'errors': e.args[0]}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
