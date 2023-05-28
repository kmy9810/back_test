from django.db import models
from django.utils import timezone
from users.models import User
from django.urls import reverse

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # 다른 필드들을 필요에 따라 추가할 수 있습니다.
    point = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"결제 금액:{self.amount} Point: {self.point}"


class Subscribe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_set')
    price = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=50)
    is_subscribe = models.BooleanField(default=False)
    start_subscribe_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, default=None, blank=True)
    duration = models.IntegerField(default=0)  # 구독 기간 (일 수)

    # 구독 만료일 계산 
    def calculate_end_date(self):
        if self.type == '베이직 이용권':
            duration = 30  # 베이직 이용권 기간 (30일)
        elif self.type == '프리미엄 이용권':
            duration = 90  # 프리미엄 이용권 기간 (90일)
        else:
            duration = 0  # 이외의 경우 기간을 0으로 설정하거나 에러 처리

        end_date = self.start_subscribe_at + timezone.timedelta(days=duration)
        self.end_date = end_date  # end_date 필드 업데이트
        self.duration = duration
        self.save()  # 변경사항 저장
        return end_date

    # # 로그인 시 구독 만료 체크 
    def check_subscription_status(self):
        if self.end_date is None:
            self.calculate_end_date()  # end_date가 None인 경우 calculate_end_date() 호출하여 설정
        if self.end_date < timezone.now():
            self.user.is_subscribe = False
            self.user.save()
        return self.user.is_subscribe
