from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
import json
import time
import docx2txt
from datetime import datetime
import requests

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
    gen_time=time.time()
    key=request.GET.get('key')
    ip=request.META.get('REMOTE_ADDR')
    fernet=Fernet(key)
    enc_ip=fernet.encrypt(ip.encode())
    enc_date=fernet.encrypt(str(gen_time).encode())
    acc_token=enc_ip.decode()+" "+enc_date.decode()
    array={'Statut':'Success','access_token':acc_token,'date':date,'Valid':'3600s'}
    res=json.dumps(array)
    return HttpResponse(res)


#verify the ip adress of client and token validity 
def verify(request,key,token):
    #now = datetime.now()
    #dt_string=now.strftime("%d%m%Y%H%M%S")
    end=time.time()
  
    token_to_split=str(token).split(" ")
    enc_ip=token_to_split[0]
    enc_date=token_to_split[1]
    fernet=Fernet(key)
    ip=request.META.get('REMOTE_ADDR')
    client_ip=fernet.decrypt(enc_ip).decode()
    client_issue_date=fernet.decrypt(enc_date).decode()
    flag=True
    Reason=""
    if(end-float(client_issue_date)>=3600):
        flag=False
        Reason+=" Token Expired,"
    if(client_ip!=ip):
        flag=False
        Reason+=" Wrong ip,"
    if(flag==True):
         array={'Status':'Success','Elapsed time':end-float(client_issue_date),'Time Left':3600-(end-float(client_issue_date))}
    else:
        array={'Status':'Failed','Reason':Reason}
   
    return array

# Conversion du fichier word en text brute
def convert(request):
    key=request.GET.get('key')
    token=request.GET.get('token')
    array=verify(request,key,token)
    if (array['Status']=='Success'):
        file=request.GET.get('file')
        # Define Variable
        text = docx2txt.process(file)
        
        
        # Create Dictionary
        value = {
            "text": text
            
        }
    else:
        value={
            "text":array['Reason']
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
            data=api_google(line)
            phrase=line.split(" ")
            descriptions=[]
            titles=[]
            score_titles=[]
            # Scans data and fills titles with each title and description with each description
            
            for d in range(len(data)-1):
                titles.append({'title':data[d]['title']})
                descriptions.append({'description':data[d]['description']})
                           
            
            
            for title in titles:
                words=str(title).split(" ")
                count=0
                for i in range(len(words)):
                    
                    for j in range(len(phrase)):
                        if (words[i].lower()==phrase[j].lower()):
                            count+=1
                score_titles.append({'title':title,'Score':count})
            
        return HttpResponse(json.dumps(data))
def api_google(query):
   
    url='https://www.googleapis.com/customsearch/v1/siterestrict?key=AIzaSyCWkJSbEuouJRt-1SynRTEZJyoF4DAreQg&cx=d64bab4780ada4a44&q='+query
    response=requests.get(url)
    response.encoding='UTF-8'
    
    data=response.json()
    total_res=data['queries']['request'][0]['totalResults']
    
    
    items=data['items']
    value=[]
    i=1
    for item in items:
      value.append({'index':i,'title':item['title'],'description':item['snippet']})  
      i+=1

    value.append({'total_results':total_res})
    return value


 