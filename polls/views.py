from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
import json
import docx2txt
from datetime import datetime

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

#Generate an encription Key 
def enc_key(request):
    k = Fernet.generate_key()
    c={"key": k.decode() }
    key=json.dumps(c)

    
    return HttpResponse(key)


#Generate access token for requested key 
def access_token(request):
    now = datetime.now()
    date=now.strftime("%d-%m-%Y-%H:%M:%S")
    dt_string=now.strftime("%d%m%Y%H%M%S")
    key=request.GET.get('key')
    ip=request.META.get('REMOTE_ADDR')
    fernet=Fernet(key)
    enc_ip=fernet.encrypt(ip.encode())
    enc_date=fernet.encrypt(dt_string.encode())
    acc_token=enc_ip.decode()+" "+enc_date.decode()
    array={'Statut':'Success','access_token':acc_token,'date':date,}
    res=json.dumps(array)
    return HttpResponse(res)


#verify the ip adress of client and token validity 
def verify(request):
    now = datetime.now()
    dt_string=now.strftime("%d%m%Y%H%M%S")
    key=request.GET.get('key')
    token=request.GET.get('token')
    token_to_split=str(token).split(" ")
    enc_ip=token_to_split[0]
    enc_date=token_to_split[1]
    fernet=Fernet(key)
    client_ip=fernet.decrypt(enc_ip).decode()
    client_issue_date=fernet.decrypt(enc_date).decode()
    array={'ip':client_ip,'date_of_issue':client_issue_date}
    return HttpResponse(json.dumps(array))

# Conversion du fichier word en text brute
def convert(request):
    file=request.GET.get('file')
    # Define Variable
    text = docx2txt.process(file)
    
    
    # Create Dictionary
    value = {
        "text": text
        
    }
 
    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
    return HttpResponse(json.dumps(value))

#Segmentation du texte en ligne 
def split_text(request):
        text=request.GET.get('text')
        lines=str(text).split('.')
        value=[]
        i=1
        for line in lines :
            value.append({i:line})
            i+=1
        return HttpResponse(json.dumps(value))

 