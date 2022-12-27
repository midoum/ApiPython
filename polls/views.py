from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
import json

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def enc_key(request):
    k = Fernet.generate_key()
    c={"key": k.decode() }
    key=json.dumps(c)

    
    return HttpResponse(key)
def access_token(request):
    
    key=Fernet.generate_key()
    ip=request.META.get('REMOTE_ADDR')
    fernet=Fernet(key)
    acc_token=fernet.encrypt(ip.encode())
    array={'Statut':'Success','access token':acc_token.decode(),}
    res=json.dumps(array)
    return HttpResponse(res)