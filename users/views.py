import requests
import os
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.naver import views as naver_view
from allauth.socialaccount.providers.github import views as github_view
from django.http import HttpResponse, JsonResponse
from json.decoder import JSONDecodeError
from rest_framework import status
from users.models import User
from rest_framework.views import APIView
from users.serializers import UserSerializer, LoginSerializer
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponseRedirect


BASE_URL = 'http://127.0.0.1:8000/'
KAKAO_CALLBACK_URI = BASE_URL + 'users/kakao/callback/'
GOOGLE_CALLBACK_URI = BASE_URL + 'users/google/callback/'
NAVER_CALLBACK_URI = BASE_URL + 'users/naver/callback/'
GITHUB_CALLBACK_URI = BASE_URL + 'users/github/callback/'

state = os.environ.get('STATE')

# 일반 회원가입
class SignupView(APIView):
    def post(self, request):
        data = request.data.copy()
        serializer = UserSerializer(data=data)
        print(data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': ' 가입완료!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': f'${serializer.errors}'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


def generate_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


# KAKAO_REST_API_KEY json파일 형태로 보관하여 연결
def kakao_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    rest_api_key = os.environ.get('KAKAO_REST_API_KEY')
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = os.environ.get('KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")

    token_req_json = token_req.json()
    error = token_req_json.get("error", None)

    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get("access_token")

    """
    u_id Request
    """

    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()

    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    # kakao_account = profile_json.get('kakao_account')

    id = profile_json.get('id')
    """
    Signup or Signin Request
    """
    try:
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(uid=id)
        user = social_user.user

        # 소셜 유저가 아니거나 소셜 유저이지만 카카오 계정이 아닐 때 에러처리
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # # 다른 SNS로 가입된 유저
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        # 기존에 kakao로 가입된 유저
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(
            f"{BASE_URL}users/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)
        jwt_token = generate_jwt_token(user)
        accept_json['token'] = jwt_token

        # JWT 토큰 발급 후 redirect
        jwt_token = generate_jwt_token(user)
        response = HttpResponseRedirect("http://127.0.0.1:5500/index.html")
        response.set_cookie('jwt_token', jwt_token)
        return response
        # return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 기존에 해당 닉네임으로 가입된 유저가 없으면 새로 가입 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/users/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            response = HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            response['Location'] = "http://127.0.0.1:5500/index.html"
            return response

        # JWT 토큰 발급
        jwt_token = generate_jwt_token(user)
        response = HttpResponseRedirect("http://127.0.0.1:5500/index.html")
        response.set_cookie('jwt_token', jwt_token)
        return response


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


# Google 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')

    # 1. 받은 code로 구글에 access token 요청
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}"
        f"&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")

    # 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    # 1-2. 에러 발생 시 종료
    if error is not None:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "error"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)

    # 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    # 2-1. 에러 발생 
    if email_req_status != 200:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "failed_to_get"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)
    
    # 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    print(email_req_json)
    # {'issued_to': '250779783110-rje0f539a4ngd3qmi1ol8kr4r2n84gh1.apps.googleusercontent.com', 
    #  'audience': '250779783110-rje0f539a4ngd3qmi1ol8kr4r2n84gh1.apps.googleusercontent.com', 
    #  'user_id': '106153673973080847339', 'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid', 
    #  'expires_in': 3598, 'email': 'oky07031217@gmail.com', 'verified_email': True, 'access_type': 'offline'}

    # 3. 전달받은 이메일, access_token, code로 회원가입 or 로그인 진행
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user) # uid = 117363005248882848468

        # 소셜 유저가 아니거나 소셜 유저이지만 구글계정이 아닐 때 에러처리
        if social_user is None:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 204
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)

        if social_user.provider != 'google':
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 400
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)

        # 기존에 Google로 가입된 유저 => 로그인 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 에러가 발생하여 로그인 실패
        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "failed_to_signin"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)

        # JWT 토큰 발급
        jwt_token = generate_jwt_token(user)
        response = HttpResponseRedirect("http://127.0.0.1:5500/index.html")
        response.set_cookie('jwt_token', jwt_token)
        
        print(jwt_token)
        print("#############")
        accept_json = accept.json()
        print(accept_json)
        return response

    except User.DoesNotExist:
        # 기존에 해당 이메일로 가입된 유저가 없으면 새로 가입 => 새로 회원가입 
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/google/login/finish/", data=data)
        accept_status = accept.status_code
        
        # 에러가 발생하여 회원가입 실패
        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "google_signup"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)
        
        # 회원가입 완료!
        redirect_url = 'http://127.0.0.1:5500/index.html'
        status_code = 201
        redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
        return redirect(redirect_url_with_status)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


class MyPage(APIView):
    pass


# Naver 로그인
def naver_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=STATE_STRING&redirect_uri={NAVER_CALLBACK_URI}")


def naver_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_NAVER_SECRET")
    code = request.GET.get("code")
    state_string = request.GET.get("state")

    token_request = requests.get(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state_string}")
    token_response_json = token_request.json()

    error = token_response_json.get("error", None)
    if error is not None:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "error"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)

    access_token = token_response_json.get("access_token")

    profile_request = requests.post(
        "https://openapi.naver.com/v1/nid/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    email = profile_json.get("response").get("email")

    if email is None:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "failed_to_get"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)

    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user is None:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 204
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)
        
        if social_user.provider != 'naver':
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 400
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "failed_to_signin"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)

        jwt_token = generate_jwt_token(user)
        response = HttpResponseRedirect("http://127.0.0.1:5500/index.html")
        response.set_cookie('jwt_token', jwt_token)
        return response

    except User.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/naver/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "naver_signup"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)
        
        redirect_url = 'http://127.0.0.1:5500/index.html'
        status_code = 201
        redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
        return redirect(redirect_url_with_status)

class NaverLogin(SocialLoginView):
    adapter_class = naver_view.NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client


# Github 로그인
def github_login(request):
    client_id = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={GITHUB_CALLBACK_URI}"
    )


def github_callback(request):
    client_id = os.environ.get('SOCIAL_AUTH_GITHUB_CLIENT_ID')
    client_secret = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
    code = request.GET.get('code')

    token_req = requests.post(
        f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}&accept=&json&redirect_uri={GITHUB_CALLBACK_URI}&response_type=code", headers={'Accept': 'application/json'})
    token_req_json = token_req.json()
    error = token_req_json.get("error")
 
    if error is not None:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "error"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)
    
    access_token = token_req_json.get('access_token')

    user_req = requests.get(f"https://api.github.com/user",
                            headers={"Authorization": f"Bearer {access_token}"})
    user_json = user_req.json()
    error = user_json.get("error")
   
    if error is not None:
        redirect_url = 'http://127.0.0.1:5500/index.html'
        err_msg = "error"
        redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
        return redirect(redirect_url_with_status)

    id = user_json.get("id")
    print(user_json)

    try:
        social_user = SocialAccount.objects.get(uid=id)
        user = social_user.user

        if social_user is None:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 204
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)
        
        if social_user.provider != 'github':
            redirect_url = 'http://127.0.0.1:5500/index.html'
            status_code = 400
            redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
            return redirect(redirect_url_with_status)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/github/login/finish/", data=data)
        accept_status = accept.status_code
        
        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "failed_to_signin"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)
        
         # JWT 토큰 발급
        jwt_token = generate_jwt_token(user)
        response = HttpResponseRedirect("http://127.0.0.1:5500/index.html")
        response.set_cookie('jwt_token', jwt_token)
        return response

    except User.DoesNotExist:
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}users/github/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            redirect_url = 'http://127.0.0.1:5500/index.html'
            err_msg = "github_signup"
            redirect_url_with_status = f'{redirect_url}?err_msg={err_msg}'
            return redirect(redirect_url_with_status)
        
        redirect_url = 'http://127.0.0.1:5500/index.html'
        status_code = 201
        redirect_url_with_status = f'{redirect_url}?status_code={status_code}'
        return redirect(redirect_url_with_status)


class GithubLogin(SocialLoginView):
    adapter_class = github_view.GitHubOAuth2Adapter
    callback_url = GITHUB_CALLBACK_URI
    client_class = OAuth2Client


class UserDelete(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user == user:
            user.delete()
            return Response('삭제되었습니다!', status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)
