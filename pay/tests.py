from users.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Subscribe

class SubscribeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.subscribe = Subscribe.objects.create(user=self.user, price=1000, type='베이직 이용권', duration=30)

    def test_calculate_end_date(self):
        end_date = self.subscribe.calculate_end_date()

        expected_end_date = self.subscribe.start_subscribe_at + timezone.timedelta(days=30)
        self.assertEqual(end_date, expected_end_date)
