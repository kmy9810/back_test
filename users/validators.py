import re
from rest_framework.serializers import ValidationError


def check_password(password):
    password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&^])[A-Za-z\d$@$!%*#?&^]{8,}$"
    if not re.match(password_regex, password):
        raise ValidationError('8자 이상의 영문 대/소문자, 숫자, 특수문자 조합이어야 합니다!')
    return password
