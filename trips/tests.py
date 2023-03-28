from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from http.cookies import SimpleCookie

from .models import *
from .utils import *

import uuid, json

class UserProfileTest(TestCase):

    def test_create_guest_user(self):
        device_id = uuid.uuid4()
        user = UserProfile.objects.create(device_id=device_id)

        self.assertIsNone(user.user)
        self.assertEqual(user.device_id, device_id)
        self.assertEqual(str(user), str(device_id))
        self.assertEqual(UserProfile.objects.count(), 1)

class APITest(TestCase):
    def test_optimize_plan(self):
        url = reverse('create-trip')
        data = {
            "date": "2023-04-01",
            "start_time": "12:00",
            "end_time": "20:00",
            "places": [{
                "place_name": "Zuihōden Temple",
                "place_id": "ChIJ8y-8UGkoil8ROchbu7NB2iw",
                "photo_reference": "a"
            }, {
                "place_name": "Sendai Atago Shrine",
                "place_id": "ChIJm4lp3nMoil8R8H8NilZ0eOE",
                "photo_reference": "a"
            }, {
                "place_name": "Kotodai Park",
                "place_id": "ChIJTUkzbC8oil8RDoO2KHdhc2A",
                "photo_reference": "a"
            }, {
                "place_name": "War Reconstruction and Memorial Hall",
                "place_id": "ChIJs4syYTkoil8Rkm6b6a0v9uY",
                "photo_reference": "a"
            }, {
                "place_name": "AER Observation Terrace",
                "place_id": "ChIJU5F-LiIoil8RowkTpLAUs3U",
                "photo_reference": "a"
            }]
        }
        self.client.cookies = SimpleCookie({'device': uuid.uuid4()})
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(Trip.objects.count(), 1)
        self.assertEqual(Destination.objects.count(), 5)