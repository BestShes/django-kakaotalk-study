import json

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from kakaotalk import settings


# 아직 테스트 하지 않음 카톡 셋팅을 따로 함수로 뽑아놓음
def kakao_server_settings():
    config = settings.config
    settings_file = {
        'client_id': config['kakaotalk']['rest_api_key'],
        'redirect_uri': 'http://172.30.1.10:8000/kakaotalk/login/success',
        'response_type': 'code',
    }

    return settings_file


def login(request):
    # kakao_server_settings()를 이용하여 셋팅설정을 한곳에 모은 후 리턴함 아직 테스트하지 않음
    settings_file = kakao_server_settings()
    client_id = settings_file['client_id']
    redirect_uri = settings_file['redirect_uri']
    response_type = settings_file['response_type']
    # config = settings.config
    # client_id = config['kakaotalk']['rest_api_key']
    # redirect_uri = 'http://172.30.17.16:8000/kakaotalk/login/success'
    # response_type = 'code'
    kakao_auth_url = 'https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}'.format(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type
    )
    context = {
        'kakao_auth_url': kakao_auth_url,

    }

    return render(request, 'api/index.html', context)


# 카카오톡 로그인 성공후 이쪽으로 redirect됨
def login_success(request):
    # kakao_server_settings()를 이용하여 셋팅설정을 한곳에 모은 후 리턴함 아직 테스트하지 않음
    settings_file = kakao_server_settings()
    client_id = settings_file['client_id']
    redirect_uri = settings_file['redirect_uri']
    response_type = settings_file['response_type']
    # config = settings.config
    # client_id = config['kakaotalk']['rest_api_key']
    # redirect_uri = 'http://172.30.17.16:8000/kakaotalk/login/success'
    # response_type = 'code'
    # 카카오톡 로그인에 성공하면 지정한 redirec_uri로 GET방식으로 code이름에 authorize_code값이 넘어옴
    if request.GET.get('code'):
        authorize_code = request.GET.get('code')
        # get_access_token 함수에 authorize_code를 넘김
        get_token = get_access_token(client_id, redirect_uri, authorize_code)
        # get_access_token에서 리턴받은 dictionary에서 access_token값 분리
        access_token = get_token['access_token']
        # token_type은 카톡서버에서 access_token을 원할때 같이 요구해서 미리 빼놓음
        token_type = get_token['token_type']
        # 나에게로 메세지 보내기 함수로 access_token전달
        message_send_me(access_token)

        get_profile_data(access_token)
    return render(request, 'api/success.html')


def get_access_token(client_id, redirect_uri, authorize_code):
    # login_success에서 넘어온 authorize_code를 이용해 POST형식으로 서버에 토큰들을 요구함
    params = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': authorize_code
    }
    request_user_token = requests.post('https://kauth.kakao.com/oauth/token', params=params)
    # json형식으로 넘어온 데이터를 dictionary형태로 변환
    get_user_token = request_user_token.json()
    # 넘어온 데이터에서 access_token과 token_type분리
    token = {
        'access_token': get_user_token['access_token'],
        'token_type': get_user_token['token_type']
    }
    # token dictionary 형태로 리턴
    return token


def message_send_me(access_token):
    # template_id는 카톡 개발자에서 미리 만들어둔 템플릿 아이디
    params = {
        'template_id': '2955'
    }
    # Authorization은 POST의 헤더파일에 담아서 보내야함 이것때문에 반나절은 날린듯.. Bearer다음 공백 1칸
    header = {
        'Authorization': 'Bearer ' + access_token,
    }
    result = requests.post('https://kapi.kakao.com/v1/api/talk/memo/send', headers=header, params=params)
    print(result)
    return result


def get_profile_data(access_token):
    header = {
        'Authorization': 'Bearer ' + access_token,
    }
    result = requests.get('https://kapi.kakao.com/v1/api/talk/profile', headers=header)
    profile_data = result.json()
    print(profile_data)
