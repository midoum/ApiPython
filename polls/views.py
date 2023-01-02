from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import docx2txt
from datetime import datetime
import requests
import re
import openai
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
        key=request.GET.get('key')
        token=request.GET.get('token')
        array=verify(request,key,token)
        value=[]
        if (array['Status']=='Success'):
            text=request.GET.get('text')
            lines=str(text).split('.')
            
            i=1
            
            for line in lines :
                if (i==1):
                    Flag=False
                else:
                    Flag=True
    #Loading du driver de webscraping 1 seule fois au debut = optimisation de temp de processing
                options = webdriver.ChromeOptions()
                if (Flag==False):
                    driver = webdriver.chrome.webdriver.WebDriver(executable_path='chromedriver')
            
                else :
                    options.add_argument("--headless")
                    driver = webdriver.chrome.webdriver.WebDriver(executable_path='chromedriver',chrome_options=options)
                score_description,score_title,nb_results,score_final=Score_Text(line,Flag,driver)
                value.append({'phrase':line,'Score_final':score_final})
                i+=1   
        else :
            value.append({'phrase':'Error','Score_final':array['Reason']})
        return HttpResponse(json.dumps(value))


#fonction qui enlève les characère spéciaux de chaque ligne
def removeSpecialChar(title):
    normal_string =re.sub("[^A-Z]", "", title,0,re.IGNORECASE)
    return normal_string


#fonction qui retourne le score de chaque titre et chaque description
def Score_Text(line,Flag,driver):
 
    score=0
    score_final=0
    sc_desc=0
    sc_title=0
    data_titles,data_descriptions,nb_results=Webscraping(line,Flag,driver)
    
    phrase=line.split(" ")


    descriptions=[]
    titles=[]

    score_titles=[]
    score_description=[]
    # Scans data and fills titles with each title and description with each description
    
    for d in range(len(data_titles)-1):
        titles.append({'title':data_titles[d]})
        descriptions.append({'description':data_descriptions[d]})
                    
    
    
    for title in titles:
        
        words=str(title['title']).split(" ")
        count=0
        for i in range(len(words)):
            
            for j in range(len(phrase)):
                if (words[i].lower()==phrase[j].lower()):
                    count+=1
        score_titles.append({'title': title['title'],'Score':count})
    for desc in descriptions :
        words= str(desc['description']).split(" ")
        count=0
        for i in range(len(words)):
            for j in range(len(phrase)):
                if(words[i].lower()==phrase[j].lower()):
                    count+=1
        score_description.append({'description':desc['description'],'Score':count})
    
    for i in range(len(score_description)):
        sc_desc+=int(score_description[i]['Score'])
    for i in range(len(score_titles)):
        sc_title+=int(score_titles[i]['Score'])

    score_final=sc_title+sc_desc
           
    return score_description,score_titles,nb_results,score_final 

#fonction qui utilise silinium et google web driver pour récupérer les titre et decriptions
def Webscraping(query,Flag,driver):
    
    
    
    driver.get('https://cse.google.com/cse?cx=d64bab4780ada4a44#gsc.tab=0&gsc.q='+query)
    content = driver.page_source
    soup = BeautifulSoup(content)
    titles=[]
    descriptions=[]
    nb_results=soup.find('div',attrs={'class':'gsc-result-info'})

    for res in soup.findAll('div',attrs={'class':'gsc-webResult gsc-result'}):
        title=res.find('div',attrs={'class':'gs-title'})
        desc=res.find('div',attrs={'class':'gs-bidi-start-align gs-snippet'})
        if(title!=None):
            titles.append(title.text)
            descriptions.append(desc.text)
        else:
            titles.append('')
            descriptions.append('')
    if (Flag==False):
        time.sleep(10)
    return titles,descriptions,nb_results

#fonction qui utilise openai pour générer un texte depuis un texte
def generate_title(request):
    key=request.GET.get('key')
    token=request.GET.get('token')
    array=verify(request,key,token)
    if (array['Status']=='Success'):

        text=request.GET.get('text')
        openai.api_key="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"
        response = openai.Completion.create(
        model="text-davinci-001",
        prompt="write a title from this text in french \""+text+"\"",
        temperature=0.4,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        titre=response['choices'][0]['text']
        title={'title':titre}
    else:
        title={'error':array['Reason']}
    return HttpResponse(json.dumps(title))

#fonction pour générer une description d'un texte avec openai
def generate_description(request):
    key=request.GET.get('key')
    token=request.GET.get('token')
    array=verify(request,key,token)
    if (array['Status']=='Success'):

        text=request.GET.get('text')
        openai.api_key="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"
        response = openai.Completion.create(
        model="text-davinci-001",
        prompt="write a website description from this text in french \""+text+"\"",
        temperature=0.4,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        titre=response['choices'][0]['text']
        title={'description':titre}
    else:
        title={'error':array['Reason']}
    return HttpResponse(json.dumps(title))
    

