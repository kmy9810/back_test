from django.urls import path
from . import views

urlpatterns = [
    # 일반 로그인
    path('signups/', views.SignupView.as_view(), name='signups'),
    path('logins/', views.LoginView.as_view(), name='logins'),
    # 카카오 로그인
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(),
         name='kakao_login_todjango'),
    # path('kakao/logout/', views.KakaoLogout.as_view(), name='kakao_logout'),
    # 구글 로그인
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),
    path('google/login/finish/', views.GoogleLogin.as_view(),
         name='google_login_todjango'),
    # 네이버 로그인
    path('naver/login', views.naver_login, name='naver_login'),
    path('naver/callback/', views.naver_callback, name='naver_callback'),
    path('naver/login/finish/', views.NaverLogin.as_view(),
         name='naver_login_todjango'),
    # 깃허브 로그인
    path('github/login/', views.github_login, name='github_login'),
    path('github/callback/', views.github_callback, name='github_callback'),
    path('github/login/finish/', views.GithubLogin.as_view(),
         name='github_login_todjango'),
    # 회원탈퇴
    path('delete/<int:user_id>/', views.UserDelete.as_view()),
]
