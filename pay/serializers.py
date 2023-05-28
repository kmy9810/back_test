from rest_framework import serializers
from .models import Payment, Subscribe
from rest_framework.serializers import ValidationError


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('__all__')
    
    # def validate(self, attrs):
    #     if attrs['is_subscribe']:
    #         raise ValidationError({'error': '이미 구독 중입니다!'}, code='400')

    #     return attrs