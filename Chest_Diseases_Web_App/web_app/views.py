from django.shortcuts import render,redirect,reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from tensorflow.keras.preprocessing import image
import cx_Oracle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2
import os
import smtplib as sb
# Create your views here.
cx_Oracle.init_oracle_client(r'D:\instantclient\instantclient_19_8')
conn = cx_Oracle.connect("PROJECT2", "PROJECT2", "yousef1")
cur = conn.cursor()

doctor_name=None
password =None
role =None
saved_sample=None
saved_protocol = None
image_url = None
imgs=None
chest_error=None
flag=None
ct_image_url = None
ct_imgs=None
ct_error=None
ct_flag=None
def index(request):
    contex = {'doctor_name':doctor_name,'password':password,'role':role}
    return render(request,'web_app/index.html',contex)

def login(request):
    contex={}
    if request.method == 'POST':
        cur.execute(f"select doctor_first_name,role,pass from doctor where doctor_id = {int(request.POST['doctor_id'])}")
        result =cur.fetchall()
        if result:
            if request.POST['password']==result[0][2]:
                global doctor_name,password,role
                doctor_name = result[0][0]
                role = result[0][1]
                password = result[0][2]
                return redirect(index)
            else:
                contex['error'] = 'Wrong Password'
        else:
            contex['error']='Wrong ID'

    return render(request,'web_app/login.html',contex)

def chestPage(request):
    if role ==None:
        return redirect(login)

    if request.method == 'POST':
        try:
            if request.POST['upload'] == 'Upload':
                if request.FILES:
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                    file = fs.save(request.FILES['x_ray'].name,request.FILES['x_ray'])
                    file_url = fs.url(file)
                    img = image.load_img(os.path.join('D:\pyyousef\Django_projects\grad_project_web\static\media',file), target_size=(256,256, 3))
                    img = image.img_to_array(img)
                    img = img / 255.
                    image.save_img(os.path.join('D:\pyyousef\Django_projects\grad_project_web\static\media',file),img)
                    global image_url,imgs
                    image_url=file_url
                    imgs= img
                    return redirect(chestPage)
                else:
                    error = 'Select X_ray first'
                    global chest_error
                    chest_error =error
        except:
            pass
        try:
            if request.POST['submit']=='Predict':
                if type(imgs) == np.ndarray:
                    return redirect(chest_report)
                else:
                    error = 'please upload X_ray'
                    chest_error = error
                    return redirect(chestPage)
        except:
            pass
    global flag
    if flag:
        imgs =None
        flag=False
        chest_error = None
    contex = {'doctor_name':doctor_name,'password':password,'role':role,'image_url':image_url,'error':chest_error,'imgs':imgs}
    return render(request,'web_app/chest.html',contex)

def breastPage(request):
    sample = []
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role}
    if role ==None:
        return redirect(login)
    else:
        if request.method == 'POST':
            if len(request.POST)==19:
                for key ,value in request.POST.items():
                    sample.append(value)
                sample=sample[1:]
                sample.insert(2,'1')
                if all(sample):
                    ajjc_model = load_model(r"D:\yousef\term10\Gradproject2\final_brest_stages.h5")
                    protocol_model = load_model(r"D:\yousef\term10\Gradproject2\final_brest_protocols.h5")
                    stage = ajjc_model.predict(np.expand_dims(np.array(sample,dtype=float),axis=0))
                    sample.insert(10,np.argmax(stage))
                    protocols = protocol_model.predict(np.expand_dims(np.array(sample,dtype=float),axis=0))
                    sample.append(round(np.max(stage) * 100, 2))
                    global saved_sample , saved_protocol
                    saved_sample = sample
                    saved_protocol = protocols
                    return redirect(breast_report)
                else:
                    contex['error'] = 'please fill all the fileds'

            else:
                contex['error'] = 'please fill all the fileds'

    return render(request,'web_app/breast_cancer.html',contex)

def about(request):
    contex = {'doctor_name':doctor_name,'password':password,'role':role}
    return render(request,'web_app/about_us.html',contex)

def contact(request):
    contex = {'doctor_name':doctor_name,'password':password,'role':role}
    if request.method == 'POST':
            server = sb.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login('chestpredictor.team@gmail.com','sara55751553')
            message = 'Subject {}\n\nFrom:{}\n\n{}'.format('FeedBack',request.POST['email'],request.POST['message'])
            server.sendmail(request.POST['email'],'chestpredictor.team@gmail.com',message)

    return render(request,'web_app/contact.html',contex)

def logout(request):
    global doctor_name, password, role
    doctor_name=None
    role=None
    password=None
    return redirect(login)

def breast_report(request):
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role}
    if saved_sample:
        if int(saved_sample[0]) == 1:
            contex['er_positive']='Positive'
        else:
            contex['er_positive'] = 'Negative'

        if int(saved_sample[1]) == 1:
            contex['pr_positive']='Positive'
        else:
            contex['pr_positive'] = 'Negative'
        contex['ld']=saved_sample[3]
        contex['node_no']=saved_sample[4]

        if int(saved_sample[5]) == 1:
            contex['node_coded']='Positive'
        else:
            contex['node_coded'] = 'Negative'

        if int(saved_sample[6]) == 0:
            contex['breast_quad']='Central'
        elif int(saved_sample[6])==1:
            contex['breast_quad'] = 'Left Low'
        elif int(saved_sample[6])==2:
            contex['breast_quad'] = 'Left Up'
        elif int(saved_sample[6])==3:
            contex['breast_quad'] = 'Right Low'
        else:
            contex['breast_quad'] = 'Right Up'

        if int(saved_sample[7]) == 0:
            contex['tumor_stage']='T0'
        elif int(saved_sample[7])==1:
            contex['tumor_stage'] = 'T1'
        elif int(saved_sample[7])==2:
            contex['tumor_stage'] = 'T2'
        else:
            contex['tumor_stage'] = 'T3'

        if int(saved_sample[8]) == 0:
            contex['node_type']='N0'
        elif int(saved_sample[8])==1:
            contex['node_type'] = 'N1'
        elif int(saved_sample[8])==2:
            contex['node_type'] = 'N2'
        else:
            contex['node_type'] = 'N3'

        if int(saved_sample[9]) == 0:
            contex['meta']='M0'
        else:
            contex['meta'] = 'M1'

        contex['stage']=get_ajjc(int(saved_sample[10]))
        contex['infiction_risk']=get_yes_no(saved_sample[11])
        contex['cardiec_risk'] = get_yes_no(saved_sample[12])
        contex['surgery_risk'] = get_yes_no(saved_sample[13])
        contex['chest_risk'] = get_yes_no(saved_sample[14])
        contex['thromboembolism_risk'] = get_yes_no(saved_sample[15])
        contex['sleep_apnea'] = get_yes_no(saved_sample[16])
        contex['alcohol'] = get_yes_no(saved_sample[17])
        contex['allergeis'] = get_yes_no(saved_sample[18])
        contex['smoker'] = get_yes_no(saved_sample[19])
        contex['ajjc_coff']=saved_sample[20]
        contex['hermonal']= round((saved_protocol[0][0])*100,2)
        contex['chemo'] = round((saved_protocol[0][1])*100,2)
        contex['surgery'] = round((saved_protocol[0][2])*100,2)
    return render(request,'web_app/breast_report.html',contex)

def chest_report(request):
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role}
    global image_url, flag
    labels =[]
    conf=[]
    if type(imgs) == np.ndarray:
        chest_model = load_model(r"D:\yousef\term10\Gradproject2\NIH 0.94838_modified_for_window.h5")
        output_class = chest_model.predict(np.expand_dims(imgs, axis=0))
        indexs = np.argpartition(output_class[0],-3)[-3:]
        for indx in indexs:
            labels.append(get_chest_diseas(indx))
            conf.append(round(output_class[0][indx]*100,2))
        # output_class=np.argmax(chest_model.predict(np.expand_dims(imgs,axis=0)))
        # diseas=get_chest_diseas(output_class)
        contex['image_url']=image_url
        contex['diseas1']=labels[0]
        contex['diseas2'] = labels[1]
        contex['diseas3'] = labels[2]
        contex['conf1'] = conf[0]
        contex['conf2'] = conf[1]
        contex['conf3'] = conf[2]
        image_url=None
        flag=True
    return render(request,'web_app/chest_report.html',contex)

def dashboard(request,pk):
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role}
    contex['pk']=pk
    return render(request,'web_app/dashboard.html',contex)

def ct_scans(request):
    if role == None:
        return redirect(login)

    if request.method == 'POST':
        try:
            if request.POST['upload'] == 'Upload':
                if request.FILES:
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
                    file = fs.save(request.FILES['x_ray'].name, request.FILES['x_ray'])
                    file_url = fs.url(file)
                    img = image.load_img(
                        os.path.join('D:\pyyousef\Django_projects\grad_project_web\static\media', file),
                        target_size=(224, 224, 3))
                    img = image.img_to_array(img)
                    img = img / 255.
                    image.save_img(os.path.join('D:\pyyousef\Django_projects\grad_project_web\static\media', file), img)
                    global ct_image_url, ct_imgs
                    ct_image_url = file_url
                    ct_imgs = img
                    return redirect(ct_scans)
                else:
                    error = 'Select Ct_scan first'
                    global ct_error
                    ct_error = error
        except:
            pass
        try:
            if request.POST['submit'] == 'Predict':
                if type(ct_imgs) == np.ndarray:
                    # chest_model = load_model(r"D:\yousef\term10\Gradproject2\final_chest_model.h5")
                    # output_class = chest_model.predict(np.expand_dims(ct_imgs, axis=0))
                    # indexs = np.argpartition(output_class[0], -3)[-3:]
                    # for indx in indexs:
                    #     print(get_chest_diseas(indx))
                    #     print(round(output_class[0][indx] * 100, 2))
                    # # print(output_class1)
                    # # print(diseas)

                    return redirect(ct_report)
                else:
                    error = 'please upload Ct_scan'
                    ct_error = error
                    return redirect(ct_scans)
        except:
            pass
    global ct_flag
    if ct_flag:
        ct_imgs = None
        ct_flag = False
        ct_error = None
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role, 'image_url': ct_image_url,
              'error': ct_error, 'imgs': ct_imgs}
    return render(request, 'web_app/ct_scanes.html', contex)

def ct_report(request):
    contex = {'doctor_name': doctor_name, 'password': password, 'role': role}
    global ct_image_url, ct_flag
    if type(ct_imgs) == np.ndarray:
        ct_model = load_model(r"D:\yousef\term10\Gradproject2\CT_Scan_modified_for_windows.h5")
        output_class = np.argmax(ct_model.predict(np.expand_dims(ct_imgs, axis=0)))
        diseas = get_ct_diseas(output_class)
        conf = round(np.max(ct_model.predict(np.expand_dims(ct_imgs, axis=0)))*100,2)
        # indexs = np.argpartition(output_class[0],-3)[-3:]
        # for indx in indexs:
        #     labels.append(get_chest_diseas(indx))
        #     conf.append(round(output_class[0][indx]*100,2))
        # output_class=np.argmax(chest_model.predict(np.expand_dims(imgs,axis=0)))
        # diseas=get_chest_diseas(output_class)
        contex['ct_image_url']=ct_image_url
        contex['diseas']=diseas
        contex['conf'] = conf

        ct_image_url=None
        ct_flag=True
    return render(request,'web_app/ct_report.html',contex)

def get_ajjc(encoded):
    code = {'Stage I': 0, 'Stage IIA': 1, 'Stage IIB': 2, 'Stage IIIA': 3, 'Stage IIIB': 4, 'Stage IIIC': 5,
            'Stage IV': 6}

    for x, y in code.items():
        if encoded == y:
            return x

def get_yes_no(bool):
    code={'1':'yes','0':'no'}
    return code.get(bool)

def get_chest_diseas(encoded):
    code={'Atelectasis':0,'Cardiomegaly':1,'Consolidation':2, 'Edema':3, 'Effusion':4,
       'Emphysema':5, 'Fibrosis':6, 'Hernia':7, 'Infiltration':8, 'Mass':9, 'No Finding':10,
       'Nodule':11, 'Pleural_Thickening':12, 'Pneumonia':13, 'Pneumothorax':14}
    for x, y in code.items():
        if encoded == y:
            return x


def get_ct_diseas(encoded):
    code = {'adenocarcinoma':0, 'large.cell.carcinoma':1, 'normal':2, 'squamous.cell.carcinoma':3}
    for x, y in code.items():
        if encoded == y:
            return x


