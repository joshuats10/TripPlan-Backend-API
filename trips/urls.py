from django.urls import path

from .views import OptimizeTripPlan, ListDestinations

urlpatterns = [
    path('optimize_trip/', OptimizeTripPlan.as_view(), name='create-trip'),
    path('get_trip_destinations/<uuid:pk>/', ListDestinations.as_view(), name='get-destinations')
]