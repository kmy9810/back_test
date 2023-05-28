from django.apps import AppConfig


class PayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pay'
    # def ready(self):
    #     import pay.signals  # 신호 수신기를 등록하기 위해 signals 모듈을 import합니다.