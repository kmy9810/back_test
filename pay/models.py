from django.db import models


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
    type = models.CharField(max_length=50)
    is_subscribe = models.BooleanField(default=False)
    start_subscribe_at = models.DateTimeField(auto_now_add=True)
    restart_subscribe_at = models.DateTimeField(null=True, default=None, blank=True)
    end_subscribe_at = models.DateTimeField(null=True, default=None, blank=True)
    price = models.PositiveIntegerField(default=0)