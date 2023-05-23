from django.shortcuts import render
from .models import Payment, Subscribe
import requests, json, base64, time
from django.http import HttpResponse


def success(request):
  orderId = request.GET.get('orderId')
  amount = request.GET.get('amount')
  paymentKey = request.GET.get('paymentKey')
  print(orderId,amount,paymentKey, "진입 체크")
  
  url = "https://api.tosspayments.com/v1/payments/confirm"
  secertkey = "test_sk_qLlDJaYngroLz95eAom8ezGdRpXx"
  userpass = secertkey + ':'
  encoded_u = base64.b64encode(userpass.encode()).decode()
  
  headers = {
    "Authorization" : "Basic %s" % encoded_u,
    "Content-Type": "application/json"
  }
  
  params = {
    "orderId" : orderId,
    "amount" : amount,
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
  payment = Payment.objects.create(amount=totalAmount, supplied_amount=suppliedAmount, point=(suppliedAmount * 0.03))
  subscribe = Subscribe.objects.create(price=totalAmount, is_subscribe=True, type=orderName)


  response_data = {
      'res': pretty,
      'respaymentKey': respaymentKey,
      'resorderId': resorderId,
      'totalAmount': totalAmount,
      'suppliedAmount': suppliedAmount,
      'vat': vat,
      'requestedAt': requestedAt,
      'orderName' : orderName
  }

  #   # JSON 응답을 생성
  return HttpResponse(json.dumps(response_data), content_type='application/json')




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