from users.models import User
from django.test import TestCase
from django.utils import timezone
from django.http import HttpResponse
from .models import Subscribe
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils.encoding import smart_bytes
import jwt
import os
class SubscribeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@test.com', password='testpassword')
        self.subscribe = Subscribe.objects.create(user=self.user, price=1000, type='베이직 이용권', duration=30)

    def test_calculate_end_date(self):
        end_date = self.subscribe.calculate_end_date()

        expected_end_date = self.subscribe.start_subscribe_at + timezone.timedelta(days=30)
        self.assertEqual(end_date, expected_end_date)



# class CheckSubscriptionAPITest(TestCase):
#     def setUp(self):
#         # 테스트에 필요한 사용자와 구독 정보를 생성합니다.
#         self.user = User.objects.create_user(email='test@test.com', password='testpassword')
#         self.subscription = Subscribe.objects.create(user=self.user, price=1000, type='베이직 이용권', duration=30)
#         self.client = APIClient()

#     def test_check_subscription_status(self):
#         self.client.force_authenticate(user=self.user)
#         access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg1MzUzMDAyLCJpYXQiOjE2ODUyNjY2MDIsImp0aSI6IjFmYzc2Y2M0ZWU0MjRmMjlhYjg1N2E1NzBmN2MxNWE3IiwidXNlcl9pZCI6NiwiZW1haWwiOiJ3a2RkYnJ1ZDU5QGdtYWlsLmNvbSIsImlzX3N1YnNjcmliZSI6dHJ1ZX0.7v_WBUDBTXnbeEeJpnXHjukVWmr-tNOVe5Kcrjm5O74'
#         django_secret_key = os.environ.get('SECRET_KEY')
#         decodedToken = jwt.decode(access_token, key=django_secret_key, algorithms=["HS256"]) #jwt 복호화 
#         response = self.client.get(reverse('check_subscription'), HTTP_AUTHORIZATION=f'Bearer {decodedToken}')

#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(data['is_subscribe'], self.subscription.is_subscribe)
