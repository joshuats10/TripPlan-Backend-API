from django.test import TestCase

from .models import *

import uuid

class UserProfileTest(TestCase):

    def test_create_guest_user(self):
        device_id = uuid.uuid4()
        user = UserProfile.objects.create(device_id=device_id)

        self.assertIsNone(user.user)
        self.assertEqual(user.device_id, device_id)
        self.assertEqual(str(user), str(device_id))
