from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('enc_key', views.enc_key, name='enc_key'),
    path('access_token', views.access_token, name='access_token'),
    path('verify_token',views.verify,name='verify_token'),
    path('convert',views.convert,name='convert'),
       path('split',views.split_text,name='split_text'),

]