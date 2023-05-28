from django.shortcuts import render
from .models import Payment, Subscribe
import requests, json, base64, time
from django.http import HttpResponse
import jwt
import os
from users.models import User
from users.serializers import UserSerializer
from .serializers import SubscribeSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from rest_framework.response import Response



class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["user_id"] = user.id
        token['email'] = user.email
        token['access_token'] = str(token.access_token)
        return token
        


def generate_jwt_token(user):
    refresh = CustomRefreshToken.for_user(user)
    return refresh["access_token"]
  
  
class check_subscription(APIView):
    def get(self, request):
        access_token = request.META.get('HTTP_AUTHORIZATION_TOKEN')
        django_secret_key = os.environ.get('SECRET_KEY')
        decodedToken = jwt.decode(access_token, key=django_secret_key, algorithms=["HS256"]) #jwt 복호화 
        print(access_token)
        print(decodedToken)
        user_id = decodedToken.get('user_id')
        user = User.objects.get(id=user_id)
        test = user.is_subscribe
        print(user.is_subscribe)
        flag =user.user_set.check_subscription_status()
        print(user.user_set.check_subscription_status())
        if test != user.user_set.check_subscription_status():
            print("ㅇㅇㅇ")
            # JWT 토큰 발급
            
            print("ㅇㅇㅇㅇㅇㅇㅁㄴㅇㅁㄴㅇㅁㄴㅁㄴ")
            del request.META['HTTP_AUTHORIZATION_TOKEN']
            jwt_token = generate_jwt_token(user)
            a =request.META['HTTP_AUTHORIZATION_TOKEN'] = 'Bearer ' + jwt_token
            print(a)
            # response.delete_cookie('jwt_token')
            # jwt_token = generate_jwt_token(user)
            # response.set_cookie('jwt_token', jwt_token)
            # print(jwt_token)

        return HttpResponse(status=200)

def success(request):
    access_token = request.META.get('HTTP_AUTHORIZATION_TOKEN')
    orderId = request.GET.get('orderId')
    amount = request.GET.get('amount')
    paymentKey = request.GET.get('paymentKey')

    url = "https://api.tosspayments.com/v1/payments/confirm"
    secret_key = os.environ.get('TOSS_SECRET_KEY')
    django_secret_key = os.environ.get('SECRET_KEY')
    try:
        token_data = jwt.decode(access_token, key=django_secret_key, algorithms=["HS256"]) #jwt 복호화 
        print(token_data)
        user_id = token_data.get('user_id')
        # 사용자 ID로 DB에서 user_id 가져오기 
        user = User.objects.get(id=user_id)
        user_serializer = UserSerializer(user)
        user.is_subscribe = True
        user.save()
        
        userpass = secret_key + ':'
        encoded_u = base64.b64encode(userpass.encode()).decode()

        headers = {
            "Authorization": "Basic %s" % encoded_u,
            "Content-Type": "application/json",
        }
        params = {
            "orderId": orderId,
            "amount": amount,
            "paymentKey": paymentKey,
        }

        res = requests.post(url, data=json.dumps(params), headers=headers)
        resjson = res.json()
        pretty = json.dumps(resjson, indent=4)
        respaymentKey = resjson["paymentKey"]
        resorderId = resjson["orderId"]
        suppliedAmount = resjson["suppliedAmount"]
        totalAmount = resjson["totalAmount"]
        vat = resjson["vat"]
        requestedAt = resjson["requestedAt"]
        orderName = resjson["orderName"]
        
        
        # DB에 객체 저장
        subscribe = Subscribe.objects.create(user=user, price=totalAmount, is_subscribe=True, type=orderName)
        end_date = subscribe.calculate_end_date()
        subscribe.save()
        payment = Payment.objects.create(user=user, amount=totalAmount, supplied_amount=suppliedAmount,
                                          point=(suppliedAmount * 0.03))
        payment.save()
        
        subscribe_serializer = SubscribeSerializer(subscribe)
        print(subscribe_serializer.data)
        
        response_data = {
            'res': pretty,
            'respaymentKey': respaymentKey,
            'resorderId': resorderId,
            'totalAmount': totalAmount,
            'suppliedAmount': suppliedAmount,
            'vat': vat,
            'requestedAt': requestedAt,
            'orderName': orderName,
            'user' : user_serializer.data['username'],
            'duration' : subscribe_serializer.data['duration'],
            'start_subscribe_at' : subscribe_serializer.data['start_subscribe_at'],
            'end_date' : subscribe_serializer.data['end_date']
        }

        # JSON 응답생성
        return HttpResponse(json.dumps(response_data), content_type='application/json', status=200)
    except jwt.DecodeError:
        # 잘못된 토큰 처리
        return HttpResponse(status=401)


def fail(request):
  code = request.GET.get('code')
  message = request.GET.get('message')
  
  return render(
    request,
    "payments/fail.html",
    {
      "code" : code,
      "message" : message,
    }
  )
  
  

# def subscribe(request):
#   pass

