from rest_framework import serializers

from .models import Places

class PlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = '__all__'

class DeleteAllPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('id',)

class AddPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('name', 'photo_reference')
