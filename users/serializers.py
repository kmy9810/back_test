from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_subscribe'] = user.is_subscribe
        return token

# 일반 회원가입 로그인을 위한 시리얼라이저


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("비밀번호와 비밀번호 확인이 일치하지않습니다!")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


class SocialLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_subscribe'] = user.is_subscribe
        return token