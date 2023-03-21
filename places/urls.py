from django.urls import path
from .views import getRoutes, PlacesListAPIView, PlaceDetailAPIView, AddPlaceAPIView, DeleteAllPlacesAPIView

urlpatterns = [
    path('', getRoutes, name='endpoints_list'),
    path('api/places/<uuid:pk>/', PlaceDetailAPIView.as_view(), name='place_detail'),
    path('api/places/add/', AddPlaceAPIView.as_view(), name='add_place'),
    path('api/places/delete/', DeleteAllPlacesAPIView.as_view(), name='delete_all_places'),
    path('api/places/', PlacesListAPIView.as_view(), name='place_list'),
]