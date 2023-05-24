from django.shortcuts import render
from .models import Payment, Subscribe
import requests, json, base64, time
from django.http import HttpResponse
import jwt
import os
# from user.models import User
# from user.serializers import UserSerializer

def success(request):
  access_token = request.META.get('HTTP_AUTHORIZATION_TOKEN')
  orderId = request.GET.get('orderId')
  amount = request.GET.get('amount')
  paymentKey = request.GET.get('paymentKey')
  print(orderId,amount,paymentKey, "진입 체크")
  
  url = "https://api.tosspayments.com/v1/payments/confirm"
  secret_key = os.environ.get('TOSS_SECRET_KEY')
  django_secret_key = os.environ.get('SECRET_KEY')

  try:
      token_data = jwt.decode(access_token, key=django_secret_key, algorithms=["HS256"]) #jwt 복호화 
      user_id = token_data.get('user_id')
      print("사용자 ID:", user_id)
      # 사용자 ID로 DB에서 user_id 가져오기 
      # user = User.objects.get(id=user_id)
      # user_serializer = UserSerializer(user)
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
      # suppliedAmount 값을 DB에 저장
      # subscribe = Subscribe.objects.create(user=user, price=totalAmount, is_subscribe=True, type=orderName)
      subscribe = Subscribe.objects.create(price=totalAmount, is_subscribe=True, type=orderName)
      subscribe.save()
      # payment = Payment.objects.create(user=user, amount=totalAmount, supplied_amount=suppliedAmount,
      #                                   point=(suppliedAmount * 0.03))
      payment = Payment.objects.create(amount=totalAmount, supplied_amount=suppliedAmount,
                                        point=(suppliedAmount * 0.03))
      payment.save()

      response_data = {
          'res': pretty,
          'respaymentKey': respaymentKey,
          'resorderId': resorderId,
          'totalAmount': totalAmount,
          'suppliedAmount': suppliedAmount,
          'vat': vat,
          'requestedAt': requestedAt,
          'orderName': orderName,
          # 'user' : user_serializer.data['username']
      }

      # JSON 응답생성
      return HttpResponse(json.dumps(response_data), content_type='application/json')
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