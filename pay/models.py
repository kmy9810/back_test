from django.db import models
from django.utils import timezone
# from users.models import User

class Payment(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    supplied_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # 다른 필드들을 필요에 따라 추가할 수 있습니다.
    point = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f"결제 금액:{self.amount} Point: {self.point}"


class Subscribe(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=50)
    is_subscribe = models.BooleanField(default=False)
    start_subscribe_at = models.DateTimeField(auto_now_add=True)
    restart_subscribe_at = models.DateTimeField(null=True, default=None, blank=True)
    duration = models.IntegerField(default=0)  # 구독 기간 (일 수)

    def calculate_end_date(self):
        if self.type == '베이직 이용권':
            duration = 30  # 베이직 이용권 기간 (30일)
        elif self.type == '프리미엄 이용권':
            duration = 90  # 프리미엄 이용권 기간 (90일)
        else:
            duration = 0  # 이외의 경우 기간을 0으로 설정하거나 에러 처리

        end_date = self.start_subscribe_at + timezone.timedelta(days=duration)
        # formatted_date = end_date.strftime("%Y년 %m월 %d일")
        # return formatted_date
        return end_date
      
    def check_subscription_status(self):
        end_date = self.calculate_end_date()
        if end_date < timezone.now():
            self.is_subscribe = False
            self.save()