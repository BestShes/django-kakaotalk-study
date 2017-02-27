import json
from pprint import pprint

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from kakaotalk import settings
from member.models import MyUser


def kakao_server_settings():
    """
    client_id = 카카오앱 생성시 제공받은 rest_api_key
    resirect_uri = 로그인 성공시 리다이렉트 할 경로
    response_type = code로 값 고정
    :return:
    """
    config = settings.config
    settings_file = {
        'client_id': config['kakaotalk']['rest_api_key'],
        'redirect_uri': 'http://172.30.1.10:8000/kakaotalk/login/success',
        'response_type': 'code',
    }

    return settings_file


# http://localhost:8000/kakaotalk/login으로 접속시
def login(request):
    settings_file = kakao_server_settings()
    client_id = settings_file['client_id']
    redirect_uri = settings_file['redirect_uri']
    response_type = settings_file['response_type']

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
    """

    :param request:
    get_token = get_token()에서 로그인에 성공하여 넘어온 authorize_code를 이용해 서버에서 가져온 토큰 정보를 dictionary형태로 리턴받음
    access_token = get_token값에서 access_token분리
    refresh_token = get_token값에서 refresh_token분리
    user_data = get_user_date()에서 access_token을 이용하여 서버에서 가져온 유저데이터를 dictionary형태로 리턴받음
    :return: 닉네임, 프로필사진 URL
    """
    settings_file = kakao_server_settings()
    client_id = settings_file['client_id']
    redirect_uri = settings_file['redirect_uri']
    response_type = settings_file['response_type']

    if request.GET.get('code'):
        authorize_code = request.GET.get('code')
        # get_access_token 함수에 authorize_code를 넘김
        get_token = get_tokens(client_id, redirect_uri, authorize_code)
        # get_access_token에서 리턴받은 dictionary에서 access_token값 분리
        access_token = get_token['access_token']
        # get_access_token에서 refresh_token값 분리
        refresh_token = get_token['refresh_token']
        # 나에게로 메세지 보내기 함수로 access_token전달
        message_send_me(access_token)
        # 프로필정보 가져오는 함수(id값 미포함)에 access_token전달
        get_profile_data(access_token)
        # 유저데이터 가져오는 함수(id값 포함)에 access_token전달
        user_data = get_user_data(access_token)
        # DB를 저장하는 함수에 유저데이터, access_token, refresh_token전달
        user = save_user(user_data, access_token, refresh_token)

        context = {
            'username': user_data['properties']['nickname'],
            'profile_image': user_data['properties']['profile_image']
        }
        return render(request, 'api/success.html', context)

    return render(request, 'api/index.html')


# token들을 가져오기
def get_tokens(client_id, redirect_uri, authorize_code):
    """
    request_user_token = authorize_code를 이용하여 받아온 json형태의 token정보
    get_user_token = json형태의 token정보를 dictionary형태로 변환
    :param authorize_code: 로그인 성공시 'code'라는 이름으로 넘어온 코드
    :return: get_user_token에서 access_token, refresh_token, token_type만 dictionary형태로 만들어 리턴
    """
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
    # 넘어온 데이터에서 access_token,token_type, refresh_token분리
    token = {
        'access_token': get_user_token['access_token'],
        'token_type': get_user_token['token_type'],
        'refresh_token': get_user_token['refresh_token'],
    }
    # token dictionary 형태로 리턴
    return token


# 나에게 메세지 보내기
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
    return result


# 로그인한 사용자 프로필 가져오기
def get_profile_data(access_token):
    """
    result = access_token을 이용하여 가져온 json형태의 프로필데이터
    profile_data = json형태의 프로필데이터를 dictionary형태로 변환
    :return: profile_data 리턴
    """
    header = {
        'Authorization': 'Bearer ' + access_token,
    }
    result = requests.get('https://kapi.kakao.com/v1/api/talk/profile', headers=header)
    profile_data = result.json()


# 사용자 정보 가져오기(id값 포함)
def get_user_data(access_token):
    """
    user_data_json = access_token을 이용하여 가져온 json형태의 유저데이터
    user_data = json형태의 유저데이터를 dictionary형태로 변
    :return: user_data 리턴
    """
    header = {
        'Authorization': 'Bearer ' + access_token
    }
    user_data_json = requests.post('https://kapi.kakao.com/v1/user/me', headers=header)
    user_data = user_data_json.json()
    print(user_data)
    return user_data


# DB에 유저ID, access_token, refresh_token, profile image url저장
def save_user(user_data, access_token, refresh_token):
    default = {
        'img_profile': user_data['properties']['profile_image'],
        'access_token': access_token,
        'refresh_token': refresh_token,

    }
    # DB에 유저ID에 해당하는게 있는지 확인하고 없으면 default내용까지 생성한후 해당객체와 created==False반환
    # DB에 존재하면 해당객체와 created==True반환
    user, created = MyUser.objects.get_or_create(
        name=user_data['id'],
        defaults=default
    )

    if created:
        pass
    # DB에 존재할 경우 프로필이미지와 access_token, refresh_token업데이트
    else:
        user.img_profile = user_data['properties']['profile_image']
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.save()

    return user
