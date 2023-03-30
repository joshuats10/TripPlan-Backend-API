from rest_framework import status, parsers, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from drf_spectacular.types import OpenApiTypes
from django.http import Http404
import uuid

from .models import *
from .utils import CreateTripPlan
from .serializers import *

class OptimizeTripPlan(APIView):
    parser_classes = (parsers.JSONParser,)
    
    @extend_schema(
        methods = ['POST'],
        summary = "Create optimal trip plan",
        description = "Create an optimal trip plan given some destinations chosen by the user.",
        responses = {201: TripSerializer(many=False)},
        request = {'application/json': inline_serializer(
            'CreateTrip',
            fields = {
                "date": serializers.DateField(),
                "start_time": serializers.TimeField(),
                "end_time": serializers.TimeField(),
                "places": inline_serializer(
                    'TripDestinations',
                    fields = {
                        "place_name": serializers.CharField(),
                        "place_id": serializers.CharField(),
                        "photo_reference": serializers.CharField()
                    },
                    many = True,
                )
            }
        )}
        
    )
    def post(self, request):

        data = request.data

        try:
            user = UserProfile.objects.get(user=request.user)
        except:
            device = request.COOKIES['device']
            user, created = UserProfile.objects.get_or_create(device_id=device)

        trip, created = Trip.objects.get_or_create(
            user = user, 
            date = data['date'], 
            start_time = data['start_time'],
            end_time = data['end_time']
        )

        trip_serializer = TripSerializer(trip, many=False)
        trip_plan = CreateTripPlan(data['date'], data['start_time'], data['end_time'], data['places'])
        places = trip_plan.get_optimal_trip_plan()

        for place in places:
            destination, created = Destination.objects.get_or_create(
                trip = trip,
                name = place['place_name'],
                google_place_id = place['place_id'],
                photo_id = place['photo_reference'],
                travel_order = place['travel_order'],
                arrival_time = place['arrival_time'],
                departure_time = place['departure_time'],
                stay_time = place['stay_time'],
                next_destination_mode = place['next_destination_mode'],
                next_destination_travel_time = place['next_destination_travel_time'],
            )

        return Response(trip_serializer.data, status=status.HTTP_201_CREATED)
    
class ListDestinations(APIView):
    def get_object(self, pk):
        try:
            return Trip.objects.get(pk=pk)
        except Trip.DoesNotExist:
            raise Http404
    
    @extend_schema(
        methods = ['GET'],
        summary = 'Get all destinations according to search query',
        description = 'Search for all destinations related with the same query i.e. trip_id',
        responses = {
            200: DestinationSerializer(many=True),
            404: OpenApiResponse(description='Bad Request (Trip ID not found)')
        }
    )
    def get(self, request, pk):
        trip = self.get_object(pk)
        destinations = Destination.objects.filter(trip=trip)
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)

