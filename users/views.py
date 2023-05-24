import requests
from django.conf import settings
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from rest_framework import status
from users.models import User


BASE_URL = 'http://127.0.0.1:8000/'
KAKAO_CALLBACK_URI = BASE_URL + 'users/kakao/callback/'
GOOGLE_CALLBACK_URI = BASE_URL + 'users/google/callback/'

state = getattr(settings, 'STATE')

# KAKAO_REST_API_KEY json파일 형태로 보관하여 연결


def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )

    # rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    # return redirect(
    #     f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}&prompt=create"
    # )


def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    print(rest_api_key)
    print(redirect_uri)
    print(code)
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get('kakao_account')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # print(kakao_account)
    email = kakao_account.get('email')
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    
    print(f'code = {code}')
  
    # 1. 받은 code로 구글에 access token 요청
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    
    # 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    
    # 1-2. 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)
    
    # 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')
    
    print(f'access_token  = {access_token }')
  
    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    
    # 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    
    print(email)
    
    # 3. 전달받은 이메일, access_token, code로 회원가입 or 로그인 진행
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)
        
        # 소셜 유저가 아니거나 소셜 유저이지만 구글계정이 아닐 때 에러처리
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 기존에 Google로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        print(data)
        
        accept = requests.post(
            f"http://localhost:8000/users/google/login/finish/", data=data)
        accept_status = accept.status_code
        
        
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        
        accept_json = accept.json()
        accept_json.pop('user', None)
        print(accept_json)
        return JsonResponse(accept_json) # 여기를 바꿔서 토큰을 받아오기
    
    except User.DoesNotExist:
        # 기존에 해당 이메일로 가입된 유저가 없으면 새로 가입 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code
        
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

