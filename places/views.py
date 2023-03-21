from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import Http404

from places.models import Places
from .serializers import PlacesSerializer, DeleteAllPlacesSerializer, AddPlaceSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/api/places/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of places'
        },
        {
            'Endpoint': '/api/places/<pk:id>',
            'method': ['GET', 'PUT', 'DELETE'],
            'body': None,
            'description': 'Returns a single place object (with actions: update & delete)'
        },
        {
            'Endpoint': '/api/places/add/',
            'method': 'POST',
            'body': {'name': ""},
            'description': 'Creates new place (only name) with data sent in post request'
        },
        {
            'Endpoint': '/api/places/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Delete all places'
        },
    ]
    return Response(routes)

class PlacesListAPIView(generics.ListAPIView):
    queryset = Places.objects.all()
    serializer_class = PlacesSerializer

class DeleteAllPlacesAPIView(APIView):
    def delete(self, request):
        delete_places = Places.objects.all()
        delete_places.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PlaceDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Places.objects.get(pk=pk)
        except Places.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        place = self.get_object(pk)
        serializer = PlacesSerializer(place, many=False)
        return Response(serializer.data)
    
    def put(self, request, pk):
        place = self.get_object(pk)
        serializer = PlacesSerializer(place, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        place = self.get_object(pk)
        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddPlaceAPIView(APIView):
    def post(self, request):
        data = request.data
        place = Places.objects.create(
            name = data['name']
        )
        serializer = AddPlaceSerializer(place, many=False)
        return Response(serializer.data, status.HTTP_201_CREATED)