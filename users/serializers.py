from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])
        data = {'access_token': str(refresh.access_token)}

        return data


# class UserUpdateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('password', 'phone',)

    # def update(self, instance, validated_data):
        # password = validated_data.get('password')  # password 값 가져오기
        # if password is not None:  # password 값이 존재하는 경우에만 실행
        #     user = super().update(instance, validated_data)
        #     user.set_password(password)
        #     user.save()
        # else:
        #     user = super().update(instance, validated_data)
        #     user.save()
        # return user

# 소셜 로그인 하였을 시 정보 수정은 어떻게 이루어지는가?
