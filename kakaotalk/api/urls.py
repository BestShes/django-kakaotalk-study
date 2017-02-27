from django.conf.urls import url
from . import views

app_name = 'kakaotalk'
urlpatterns = [
    url(r'login/$', views.login, name='login'),
    url(r'login/success/$', views.login_success, name='success'),
]