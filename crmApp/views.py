from django.shortcuts import render,redirect
import razorpay

from crmApp.models import *
from django.contrib.auth.models import User , auth
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import json
from  datetime import *
import os
from notifications.signals import notify
import pandas as pd
from django.db.models import Q
import pytz
import boto3
import pymongo
from boto3 import session
from botocore.client import Config
from boto3.s3.transfer import S3Transfer
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from crmproject.settings import RAZOR_KEY_ID,RAZOR_KEY_SECRET
# Create your views here.

from swapper import load_model
Notification = load_model('notifications', 'Notification')
razorpay_client = razorpay.Client(
    auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
gl_permission_eid=[]
gl_rolename_eid=[]
gl_permission_str=[]
super_user_tasks=[]


def signin(request):
    return render(request,'pages-sign-in.html')

def dashboard(request):

    username = None
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request,'index.html')
        else:
            username = request.user.username
            emp_det=login.objects.get(username=username)
            emp_ids=employee.objects.get(pk=emp_det.emp_id.id)
            att_det=attendanceTable.objects.filter(Q(att_employee_id=emp_ids.pk) & Q(att_date=date.today()))
        
            if att_det.exists():
                pass
            else:
                att_det=attendanceTable(att_employee_id=emp_ids,att_employee_name=emp_det.emp_id.e_name,att_date=date.today(),att_status="Absent")
                att_det.save()

            det=attendanceTable.objects.all().filter(Q(att_employee_id=emp_ids.pk) & Q(att_date=date.today()))
            for i in det:
                context={'status':i.att_status}

            return render(request,'index.html',context)


def mark_attendance(request):

    if request.method=='POST':

        attendance=request.POST['attendance']

        username=request.user.username
        emp_det=login.objects.get(username=username)
        emp_ids=employee.objects.get(pk=emp_det.emp_id.id)

        tz = pytz.timezone('Asia/Kolkata')
        time_now = datetime.now(tz).strftime("%H:%M:%S")
        
        attendanceTable.objects.filter(Q(att_employee_id=emp_ids.pk) & Q(att_date=date.today())).update(att_time=time_now,att_status=attendance)

        return redirect('dashboard')



def index(request):
    if request.method == "POST":
        username = request.POST["username"]
        password  = request.POST["password"]

        user = auth.authenticate(username = username,password = password)
        if user is not None:

            auth.login(request,user)
            return redirect('dashboard')

        else:
            messages.info(request,'Invalid Credentials')
            return redirect('signin')
    else:
        return render(request,'pages-sign-in.html')

def logout(request):
    auth.logout(request)
    return redirect('signin')


def show_clients_cards(request):

    user_name=request.user.username
    if request.user.is_superuser:
        entries = client.objects.all().order_by('-id')[0:5]
        context={
            'entries':entries
        }
        return render(request,'show_clients_cards.html',context)

    else:
        user_det=login.objects.filter(username=user_name)
        for i in user_det:

            if((i.role_id.name).lower()=='admin'):

                entries = client.objects.all().order_by('-id')[0:5]
                context={
                    'entries':entries
                }
                return render(request,'show_clients_cards.html',context)

            elif((i.role_id.name).lower()=='marketing executive'):

                entries = client.objects.all().filter(c_created_by='Marketing Executive').order_by('-id')[0:5]
                context={
                    'entries':entries
                }
                return render(request,'show_clients_cards.html',context)
def pay(request):
    currency = 'INR'
    amount = 20000  # Rs. 200
   
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = 'rzp_test_mp6XqYww4VvFdI'
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'pay.html', context=context)
 
 
# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.

def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()

def show_clients(request):

    user_name=request.user.username
    if request.user.is_superuser:

        entries = client.objects.all()
        context={
            'entries':entries,
        }
        return render(request,'show_clients.html',context)

    else:
        user_det=login.objects.filter(username=user_name)
        for i in user_det:

            if((i.role_id.name).lower()=='admin'):
                entries = client.objects.all()
                context={
                    'entries':entries,
                }
                return render(request,'show_clients.html',context)

            elif((i.role_id.name).lower()=='marketing executive'):

                entries = client.objects.all().filter(c_created_by='Marketing Executive')
                context={
                    'entries':entries,
                }
                return render(request,'show_clients.html',context)

def create_client(request):
    if request.method == 'POST':
        c_name = request.POST['c_name']
        c_email = request.POST['c_email']
        c_num = request.POST['c_num']
        c_univ = request.POST['c_univ']
        if c_name:
            try:
                client_email = client.objects.get(c_email=c_email)
            except client.DoesNotExist:
                client_email = None
            if client_email is not None:
                entries = client.objects.all()[0:4]
                context={
                    'messages':'Client Already Exists',
                    'entries': entries,
                }
                
                return render(request,'show_clients_cards.html',context)
            else:

                user_name=request.user.username
                if request.user.is_superuser:
                    new_client = client(c_name=c_name,c_email=c_email,c_num=c_num,c_university=c_univ,c_created_by='admin')
                    new_client.save()
                    return redirect('show_clients')    

                else:
                    user_det=login.objects.filter(username=user_name)
                    for i in user_det:

                        if((i.role_id.name).lower()=='admin'):

                            new_client = client(c_name=c_name,c_email=c_email,c_num=c_num,c_university=c_univ,c_created_by='admin')
                            new_client.save()
                            return redirect('show_clients')

                        elif((i.role_id.name).lower()=='marketing executive'):

                            new_client = client(c_name=c_name,c_email=c_email,c_num=c_num,c_university=c_univ,c_created_by='Marketing Executive')
                            new_client.save()
                            return redirect('show_clients')


def show_tasks(request):

    user_name=request.user.username
    if request.user.is_superuser:

        entries = task.objects.all()
        ids  = client.objects.all()
        employee_det=employee.objects.all()
        context={
            'entries':entries,
            'ids':ids,
            'employee_det':employee_det,
            }
        return render(request,'show_tasks.html',context) 

    else:
        user_det=login.objects.filter(username=user_name)
        for i in user_det:

            if((i.role_id.name).lower()=='admin' or (i.role_id.name).lower()=='sr'):

                entries = task.objects.all()
                ids  = client.objects.all()
                employee_det=employee.objects.all()
                context={
                    'entries':entries,
                    'ids':ids,
                    'employee_det':employee_det,
                    }
                return render(request,'show_tasks.html',context)

            elif((i.role_id.name).lower()=='marketing executive'):

                entries = task.objects.all().filter(t_created_by='Marketing Executive')
                ids  = client.objects.all().filter(c_created_by='Marketing Executive')
                employee_det=employee.objects.all()
                context={
                    'entries':entries,
                    'ids':ids,
                    'employee_det':employee_det,
                    }
                return render(request,'show_tasks.html',context)

        else:
            return render(request,'show_tasks.html')

def show_client_details(request,pk):

    client_details= client.objects.all().filter(id=pk)
    client_task_details= task.objects.all().filter(client_id=pk)

    amount=[]
    sum=0
    for i in client_task_details:
        en=int(i.t_amount)
        amount.append(en)
    for j in amount:
        sum=sum+j

    for i in client_details:
        desc = ""
        var12 =desc.split('\n')
       	print(var12)
        
    context={
        'client_details':client_details,
        'client_task_details':client_task_details,
        'sum':sum,
        'var12':var12
    }
    return render(request,'show_client_details.html',context)

def create_task(request):
    
    if request.method=="POST":
        t_name = request.POST['t_name']
        t_soft = request.POST['t_soft']
        t_hard = request.POST['t_hard']
        t_amount = int(request.POST['t_amount'])
        t_currency = request.POST['currency']
        t_wc = int(request.POST['t_wc'])
        t_status = request.POST['t_status']
        uploaded_file=request.FILES.getlist('brief')
        cid = int(request.POST['c_name'])
        p_status=request.POST['p_status']
        t_desc = request.POST['t_desc']
        f_desc = ""
        paid_amount= request.POST['paid_amount']

        if paid_amount == '':
            paid_amount = 0
        else:
            paid_amount = int(paid_amount)

        user_name=request.user.username
        if request.user.is_superuser:
            new_task = task(t_name=t_name,t_soft=t_soft,t_hard=t_hard,t_amount=t_amount,t_currency=t_currency ,t_wc = t_wc,t_status=t_status, t_desc = t_desc, client_id_id=cid,t_created_by='admin')
            new_task.save()
        else:
            user_det=login.objects.filter(username=user_name)
            for i in user_det:

                if((i.role_id.name).lower()=='admin'):
                    new_task = task(t_name=t_name,t_soft=t_soft,t_hard=t_hard,t_amount=t_amount,t_currency=t_currency ,t_wc = t_wc,t_status=t_status, t_desc = t_desc, client_id_id=cid,t_created_by='admin')
                    new_task.save()
                elif((i.role_id.name).lower()=='marketing executive'):
                    new_task = task(t_name=t_name,t_soft=t_soft,t_hard=t_hard,t_amount=t_amount,t_currency=t_currency ,t_wc = t_wc,t_status=t_status, t_desc = t_desc, client_id_id=cid,t_created_by='Marketing Executive')
                    new_task.save()

        all_ids=task.objects.values_list('id',flat=True)
        all=list(int(x) for x in all_ids)
        max_val=max(all)

        session = boto3.session.Session()
        client = session.client('s3',
                        region_name='ams3',
                        endpoint_url='https://ams3.digitaloceanspaces.com',
                        aws_access_key_id='DO00AL7HLKMKN4ATCBXH',
                        aws_secret_access_key='dAg4Iatdq9g5a9W+7Vhig1jeAOKWbZEY9Zb2kKCOhLY')

        for f in uploaded_file:
            fs=FileSystemStorage()
            file_name=fs.save(f.name,f)
            # file_url=fs.url(file_name)

            curr=os.getcwd()
            curr1=os.path.join(curr,file_name)
            #print(curr1)
    
            client.upload_file(curr1 ,  # Path to local file
                                'crmappa',  # Name of Space
                                'crm-spaces-static/media/'+file_name)  # Name for remote file
           
            
            file_url = client.generate_presigned_url(ClientMethod='get_object',
                                    Params={'Bucket': 'crmappa',
                                            'Key': 'crm-spaces-static/media/'+file_name},
                                    ExpiresIn=60*60*24*7)

            fs.delete(file_name)

            task_ids=task.objects.get(id=max_val)
            new_task_brief=filesBrief(task_id=task_ids,f_link=file_url,f_name=file_name,f_desc = f_desc) 
            new_task_brief.save()
        
        payment_create=task.objects.all().filter(id=max_val)

        task_ids=task.objects.get(id=max_val)
        
    
        for i in payment_create: 
            
            amount=int(i.t_amount)
            due_amount = amount - int(paid_amount)
            today = date.today()
            now = datetime.now()
            current_time =  now.strftime("%H:%M:%S")

            user_name=request.user.username
            if request.user.is_superuser:
                new_payment=payment(due_amount=due_amount,p_status=p_status,task_id=task_ids,p_date=today,p_time=current_time,p_created_by='admin')
                new_payment.save()
            else:
                user_det=login.objects.filter(username=user_name)
                for i in user_det:

                    if((i.role_id.name).lower()=='admin'):
                        new_payment=payment(due_amount=due_amount,p_status=p_status,task_id=task_ids,p_date=today,p_time=current_time,p_created_by='admin')
                        new_payment.save()
                    elif((i.role_id.name).lower()=='marketing executive'):
                        new_payment=payment(due_amount=due_amount,p_status=p_status,task_id=task_ids,p_date=today,p_time=current_time,p_created_by='Marketing Executive')
                        new_payment.save()

        return redirect('/show_tasks')

    else:
        task_details=task.objects.all()
        context={
        'entries':task_details,
                }

        return render(request,'show_tasks.html',context)

def show_payments(request):

    user_name=request.user.username
    if request.user.is_superuser:
        payments = payment.objects.all()
        context={
            'entries': payments,
        }
        return render(request,'show_payments.html',context)
    else:
        user_det=login.objects.filter(username=user_name)
        for i in user_det:

            if((i.role_id.name).lower()=='admin'):
                payments = payment.objects.all()
                context={
                    'entries': payments,
                }
                return render(request,'show_payments.html',context)
            elif((i.role_id.name).lower()=='marketing executive'):
                payments = payment.objects.all().filter(p_created_by='Marketing Executive')
                context={
                    'entries': payments,
                }
                return render(request,'show_payments.html',context)

def update_client(request,pk):

    entries = client.objects.all()
    client1=client.objects.all().filter(id=pk)
    
    context={
        'entries':entries,
        'client':client1
    }
    return render(request,'update_client.html',context)

def updated(request,pk):
    if request.method=="POST":
        c_name = request.POST['name']
        c_email = request.POST['email']
        c_num = request.POST['num']
        c_univ = request.POST['univ']
      
        
        client.objects.filter(id=pk).update(c_name=c_name,c_email=c_email,c_num=c_num)
        entries=client.objects.all()
        
        return redirect('/show_clients')

def update_task(request,pk):

    entries = task.objects.all()
    task1=task.objects.all().filter(id=pk)
    for entry in task1:
        cid = entry.client_id.id
        amount = int(entry.t_amount)

    entries2= payment.objects.all().filter(task_id = pk)
    for e in entries2:
        due_amt = int(e.due_amount)

    paid_amt = amount - due_amt   
    
    l=[]

    for i in task1:
        sd=str(i.t_soft)
        hd=str(i.t_hard)
        l.append(sd)
        l.append(hd)

    context={
        'entries':entries,
        'task':task1,
        'c': l[0],
        'd': l[1],
        'p':paid_amt
    }
    l.clear()
    return render(request,'update_task.html',context)

def updated_task(request,pk):
    if request.method=="POST":
        t_name = request.POST['t_name']
        t_wc = request.POST['t_wc']
        t_soft = request.POST['t_soft']
        t_hard = request.POST['t_hard']
        t_amt = request.POST['t_amt']
        t_status = request.POST['t_status']
        p_status = request.POST['p_status']
        p_amt = request.POST['p_amt']
        t_desc = request.POST['t_desc']
        due_amount =  int(t_amt) - int(p_amt)

        task.objects.filter(id=pk).update(t_name=t_name,t_wc=t_wc,t_soft=t_soft,t_hard=t_hard,t_amount=t_amt,t_status=t_status,t_desc=t_desc)
        payment.objects.filter(task_id=pk).update(p_status=p_status,due_amount=due_amount)
        entries=task.objects.all()
        
        return redirect('/show_tasks')

def update_payment(request,pk):

    entries = payment.objects.all()
    payment1=payment.objects.all().filter(task_id=pk)
    l=[]

    for i in payment1:
        sd=str(i.p_date)
        l.append(sd)

    context={
        'payment':payment1,
        'c': l[0],
    }
    l.clear()
    return render(request,'update_payment.html',context)

def updated_payment(request,pk):
    if request.method=="POST":
        p_date = request.POST['p_date']
        due_amt = request.POST['due_amt']
        p_status = request.POST['p_status']

        payment.objects.filter(id=pk).update(p_date=p_date,due_amount=due_amt,p_status=p_status)
        return redirect('/show_payments')

def show_task_details(request,pk):

    task_details = task.objects.all().filter(id=pk)
    brief_details = filesBrief.objects.all().filter(task_id=pk)
    solution_details=solutionFile.objects.all().filter(task_id=pk)
    user_details=login.objects.all()
    superusers=User.objects.filter(is_superuser=True)
    all_comments=comments.objects.filter(from_username=request.user.username,task_id=pk) | comments.objects.filter(to_username=request.user.username,task_id=pk)
    context={
        'task_details':task_details,
        'brief_details':brief_details,
        'solution_details':solution_details,
        'user_details':user_details,
        'all_comments':all_comments,
        'superusers':superusers,
        }
    return render(request,'show_task_details.html',context)

def upload_new_brief(request,pk,id):

    if request.method=="POST":
        uploaded_file = request.FILES.getlist('brief')

        session = boto3.session.Session()
        client = session.client('s3',
                        region_name='ams3',
                        endpoint_url='https://ams3.digitaloceanspaces.com',
                        aws_access_key_id='DO00AL7HLKMKN4ATCBXH',
                        aws_secret_access_key='dAg4Iatdq9g5a9W+7Vhig1jeAOKWbZEY9Zb2kKCOhLY')

        for f in uploaded_file:
            fs=FileSystemStorage()
            file_name=fs.save(f.name,f)
            #file_url=fs.url(file_name)

            curr=os.getcwd()
            curr1=os.path.join(curr,file_name)

            client.upload_file(curr1 ,  # Path to local file
                                'crmappa',  # Name of Space
                                'crm-spaces-static/media/'+file_name)  # Name for remote file
           
            file_url = client.generate_presigned_url(ClientMethod='get_object',
                                    Params={'Bucket': 'crmappa',
                                            'Key': 'crm-spaces-static/media/'+file_name},
                                    ExpiresIn=60*60*24*7)

            fs.delete(file_name)

            task_ids=task.objects.get(id=id)
            new_task_brief=filesBrief(task_id=task_ids,f_link=file_url,f_name=file_name) 
            new_task_brief.save()

        str1="/show_task_details/"+str(id)
        return redirect(str1)

def delete_brief(request,pk,id):

    brief_details=filesBrief.objects.all().filter(id=pk)
    for i in brief_details:
        b = cancelledBrief(cbf_name=i.f_name,cbf_desc=i.f_desc,cbf_link=i.f_link.name,task_id=i.task_id)
        b.save()

    filesBrief.objects.filter(id=pk).delete()

    str1="/show_task_details/"+str(id)
    
    return redirect(str1)
    
def delete_task(request,pk):
    task_details = task.objects.all().filter(id=pk)
    brief_details = filesBrief.objects.all().filter(task_id=pk)
    for i in task_details:
        cid = i.client_id.id
        client_id = client.objects.get(id = cid)
        b = cancelledTask(ctask_desc=i.t_desc,ctask_name=i.t_name,ct_hard=i.t_hard,ct_wc=i.t_wc,ct_amount = i.t_amount,client_id = client_id)
        b.save()
    
    for i in brief_details:
        task_id = task.objects.get(id = i.task_id.id)
        b = cancelledBrief(cbf_name=i.f_name,cbf_desc=i.f_desc,cbf_link=i.f_link.name,task_id=task_id)
        b.save()
    
    task.objects.filter(id=pk).delete()

    entries = task.objects.all()
    ids  = client.objects.all()
    context={
        'entries':entries,
        'ids':ids
    }
    return redirect('/show_tasks',context) 

def show_employee_cards(request):
    entries = employee.objects.all()
    ids = employee.objects.all()
    tasks = task.objects.all()
    context={
        'entries':entries,
        'ids':ids,
        'tasks':tasks,
    }
    return render(request , 'show_employee_cards.html',context)

def create_employee(request):
    if request.method == 'POST':
        e_name = request.POST['e_name']
        e_email = request.POST['e_email']
        e_num = request.POST['e_num']
        e_account_no = request.POST['e_account_no']
        e_address = request.POST['e_address']
        e_ifsc = request.POST['e_ifsc']
        if e_name:
            try:
                emp_email = employee.objects.get(e_email=e_email)
            except employee.DoesNotExist:
                emp_email = None
            if emp_email is not None:
                entries = employee.objects.all()[0:4]
                context={
                    'messages':'Employee Already Exists',
                    'entries': entries,
                }
                
                return render(request,'show_employee_cards.html',context)
            else:
                new_emp = employee(e_name=e_name,e_email=e_email,e_num=e_num,e_account_no=e_account_no,e_address=e_address,e_ifsc=e_ifsc)
                new_emp.save()
                entries = employee.objects.all()
                context={
                    'entries':entries
                    }
                return render(request,'show_employees.html',context)    

def show_employees(request):
    entries = employee.objects.all()
    context={
        'entries':entries,
    
    }
    return render(request,'show_employees.html',context)

def show_employee_details(request,pk):

    employee_details= employee.objects.all().filter(id=pk)
    for i in employee_details:
        user_det=login.objects.all().filter(emp_id=i.id)
        for j in user_det:
            if((j.role_id.name).lower()=='manager'):

                employee_task_details= assignedTaskTable.objects.all().filter(manager_id=pk)

                context={
                    'employee_details':employee_details,
                    'employee_task_details':employee_task_details,
                }
                return render(request,'show_employee_details.html',context)
            
            elif((j.role_id.name).lower()=='tl'):

                employee_task_details= assignedTaskTable.objects.all().filter(tl_id=pk)

                context={
                    'employee_details':employee_details,
                    'employee_task_details':employee_task_details,
                }
                return render(request,'show_employee_details.html',context)

            elif((j.role_id.name).lower()=='expert'):

                employee_task_details= assignedTaskTable.objects.all().filter(expert_id=pk)

                context={
                    'employee_details':employee_details,
                    'employee_task_details':employee_task_details,
                }
                return render(request,'show_employee_details.html',context)

    else:
        user_pro_details = employee.objects.all().filter(id = i.id)
        
        context = {
            'user_pro_details':user_pro_details,
                    }
        
        return render(request,'user_profile.html',context)

def update_employee(request,pk):

    employee1=employee.objects.all().filter(id=pk)
 
    context={
        'employee':employee1,
    }
    return render(request,'update_employee.html',context)

def updated_employee(request,pk):
    if request.method=="POST":
        e_name = request.POST['e_name']
        e_email = request.POST['e_email']
        e_num = request.POST['e_num']
        e_account_no = request.POST['e_account_no']
        e_address = request.POST['e_address']
        e_ifsc = request.POST['e_ifsc']

        employee.objects.filter(id=pk).update(e_name=e_name,e_email=e_email,e_num=e_num,e_address = e_address ,e_account_no=e_account_no, e_ifsc=e_ifsc)
        return redirect('/show_employees')

def delete_employee(request,pk):
    emp_details = employee.objects.all().filter(id=pk) & employee.objects.all().filter(role_id__isnull=False)
    assigned_details=''
    for i in emp_details:
        
        if((i.role_id.name).lower()=='manager'):
            assigned_details = assignedTaskTable.objects.all().filter(manager_id=pk)
        elif((i.role_id.name).lower()=='tl'):
            assigned_details = assignedTaskTable.objects.all().filter(tl_id=pk)
        else:
            assigned_details = assignedTaskTable.objects.all().filter(expert_id=pk)
            
    if(assigned_details!=''):
        for i in assigned_details:
            tid = i.task_id.id
            task.objects.filter(id = tid ).update(t_status = "unassigned")
            for j in emp_details:
                b = deletedEmployee(de_ifsc=j.e_ifsc,de_name=j.e_name,de_email=j.e_email,de_account_no = j.e_account_no, de_address = j.e_address , tasks = tid)
                b.save()
    
    employee.objects.filter(id=pk).delete()

    entries = employee.objects.all()

    context={
        'entries':entries,
    }
    return redirect('/show_employees',context) 

def assign_task(request,user_name):

    if request.method == "POST":

        taskid=request.POST['t_name']
        empid=request.POST['e_name']

        task_det=task.objects.all().filter(id=taskid)

        if(User.objects.get(username=user_name).is_superuser):

            det=login.objects.all().filter(emp_id=empid)
            for i in det:
                if((i.role_id.name).lower()=='manager'):
                    for j in task_det:
                        t_id = task.objects.get(id = taskid)
                        e_id=employee.objects.get(id=i.emp_id.id)
    # ====================================     Updating manager ID     ==========================================
                        if assignedTaskTable.objects.filter(task_id=t_id).exists():

                            data_check=assignedTaskTable.objects.filter(task_id=t_id,manager_id__isnull=False)
                            if data_check.exists():
                                assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                            else:
                                assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                        
                        else:
                            b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,manager_id=e_id,task_id=t_id)
                            b.save()
                            task.objects.filter(id=taskid).update(t_status='Assigned')

    # ===========================================================================================================
    # ============================== This is the notification part ===================================================

                        message = "New Task "+str(j.t_name)+" has been assigned to You."

                        t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                        b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                        b.save()

                        return redirect('/show_employee_cards')

    # ============================== This is the notification part ===================================================

                elif((i.role_id.name).lower()=='tl'):
                    for j in task_det:
                        t_id = task.objects.get(id = taskid)
                        e_id=employee.objects.get(id=i.emp_id.id)

    # ====================================    Updating TL ID    =====================================================
                        if assignedTaskTable.objects.filter(task_id=t_id).exists():

                            data_check=assignedTaskTable.objects.filter(task_id=t_id,tl_id__isnull=False)

                            if data_check.exists():
                                assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                            else:
                                assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')

                        else:
                            b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,tl_id=e_id,task_id=t_id)
                            b.save()
                            task.objects.filter(id=taskid).update(t_status='Assigned')
    # ===========================================================================================================

                        message = "New Task "+str(j.t_name)+" has been assigned to You."

                        t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                        b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                        b.save()

                        return redirect('/show_employee_cards')
                
                else:
                    for j in task_det:
                        t_id = task.objects.get(id = taskid)
                        e_id=employee.objects.get(id=i.emp_id.id)

    # ====================================    Updating Expert ID    ====================================================
                        if assignedTaskTable.objects.filter(task_id=t_id).exists():

                            data_check=assignedTaskTable.objects.filter(task_id=t_id,expert_id__isnull=False)
                            if data_check.exists():
                                assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                            else:
                                assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                        
                        else:
                            b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,expert_id=e_id,task_id=t_id)
                            b.save()
                            task.objects.filter(id=taskid).update(t_status='Assigned')
    # =================================================================================================================

                        message = "New Task "+str(j.t_name)+" has been assigned to You."

                        t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                        b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                        b.save()

                        return redirect('/show_employee_cards')
        else:
            details=login.objects.all().filter(username=user_name)
            for m in details:
                
                if((m.role_id.name).lower()=='admin'):
                    det=login.objects.all().filter(emp_id=empid)
                    for i in det:
                        if((i.role_id.name).lower()=='manager'):
                            for j in task_det:
                                t_id = task.objects.get(id = taskid)
                                e_id=employee.objects.get(id=i.emp_id.id)

    # ====================================     Updating manager ID     ==========================================

                                if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                    data_check=assignedTaskTable.objects.filter(task_id=t_id,manager_id__isnull=False)
                                    if data_check.exists():
                                        assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                                    else:
                                        assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                                
                                else:
                                    b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,manager_id=e_id,task_id=t_id)
                                    b.save()
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
    # =================================================================================================================

                                message = "New Task "+str(j.t_name)+" has been assigned to You."

                                t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                                b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                                b.save()
                                
                                return redirect('/show_employee_cards')

                        elif((i.role_id.name).lower()=='tl'):
                            for j in task_det:
                                t_id = task.objects.get(id = taskid)
                                e_id=employee.objects.get(id=i.emp_id.id)

    # ====================================    Updating TL ID    =====================================================
                                if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                    data_check=assignedTaskTable.objects.filter(task_id=t_id,tl_id__isnull=False)

                                    if data_check.exists():
                                        assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                                    else:
                                        assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')

                                else:
                                    b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,tl_id=e_id,task_id=t_id)
                                    b.save()
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
    # ===========================================================================================================

                                message = "New Task "+str(j.t_name)+" has been assigned to You."

                                t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                                b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                                b.save()
                                
                                return redirect('/show_employee_cards')
                        
                        else:
                            for j in task_det:
                                t_id = task.objects.get(id = taskid)
                                e_id=employee.objects.get(id=i.emp_id.id)

    # ====================================    Updating Expert ID    ====================================================
                                if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                    data_check=assignedTaskTable.objects.filter(task_id=t_id,expert_id__isnull=False)
                                    if data_check.exists():
                                        assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                                    else:
                                        assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                                
                                else:
                                    b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,expert_id=e_id,task_id=t_id)
                                    b.save()
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
    # =================================================================================================================

                                message = "New Task "+str(j.t_name)+" has been assigned to You."

                                t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                                b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                                b.save()

                                return redirect('/show_employee_cards')


                elif((m.role_id.name).lower()=='manager'):
                    det=login.objects.all().filter(emp_id=empid)
                    for i in det:
                        if((i.role_id.name).lower()=='tl'):
                            for j in task_det:
                                
                                t_id = task.objects.get(id = taskid)
                                e_id=employee.objects.get(id=i.emp_id.id)
                                m_id=employee.objects.get(id=m.emp_id.id)
                                assignedTaskTable.objects.filter(manager_id=m_id,task_id=t_id).update(tl_id=e_id)

                                message = "New Task "+str(j.t_name)+" has been assigned to You."

                                t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                                b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                                b.save()

                                # str1="/show_particular_task/"+str(user_name)
                                return redirect('/show_employee_cards')

                        elif((i.role_id.name).lower()=='expert'):
                            for j in task_det:
                                
                                t_id = task.objects.get(id = taskid)
                                e_id=employee.objects.get(id=i.emp_id.id)
                                m_id=employee.objects.get(id=m.emp_id.id)
                                assignedTaskTable.objects.filter(manager_id=m_id,task_id=t_id).update(expert_id=e_id)

                                message = "New Task "+str(j.t_name)+" has been assigned to You."

                                t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                                b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                                b.save()

                                # str1="/show_particular_task/"+str(user_name)
                                return redirect('/show_employee_cards')

                else:
                    det=login.objects.all().filter(emp_id=empid)
                    for i in det:

                        t_id = task.objects.get(id = taskid)
                        e_id=employee.objects.get(id=i.emp_id.id)
                        m_id=employee.objects.get(id=m.emp_id.id)
                        assignedTaskTable.objects.filter(tl_id=m_id,task_id=t_id).update(expert_id=e_id)

                        message = "New Task "+str(j.t_name)+" has been assigned to You."

                        t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                        b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                        b.save()

                        # str1="/show_particular_task/"+str(user_name)
                        return redirect('/show_employee_cards')


def assign_particular_task(request,user_name):
    
    taskid=request.POST['t_name']
    empid=request.POST['e_name']

    task_det=task.objects.all().filter(id=taskid)

    if(User.objects.get(username=user_name).is_superuser):

        det=login.objects.all().filter(emp_id=empid)
        for i in det:
            if((i.role_id.name).lower()=='manager'):
                for j in task_det:
                    t_id = task.objects.get(id = taskid)
                    e_id=employee.objects.get(id=i.emp_id.id)
# ====================================     Updating manager ID     ==========================================
                    if assignedTaskTable.objects.filter(task_id=t_id).exists():

                        data_check=assignedTaskTable.objects.filter(task_id=t_id,manager_id__isnull=False)
                        if data_check.exists():
                            assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                            task.objects.filter(id=taskid).update(t_status='Assigned')
                        else:
                            assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                            task.objects.filter(id=taskid).update(t_status='Assigned')
                     
                    else:
                        b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,manager_id=e_id,task_id=t_id)
                        b.save()
                        task.objects.filter(id=taskid).update(t_status='Assigned')

# ===========================================================================================================
# ============================== This is the notification part ===================================================

                    message = "New Task "+str(j.t_name)+" has been assigned to You."

                    t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                    b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                    b.save()

                    return redirect('/show_tasks')

# ============================== This is the notification part ===================================================

            elif((i.role_id.name).lower()=='tl'):
                for j in task_det:
                    t_id = task.objects.get(id = taskid)
                    e_id=employee.objects.get(id=i.emp_id.id)

# ====================================    Updating TL ID    =====================================================
                    if assignedTaskTable.objects.filter(task_id=t_id).exists():

                        data_check=assignedTaskTable.objects.filter(task_id=t_id,tl_id__isnull=False)

                        if data_check.exists():
                            assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                            task.objects.filter(id=taskid).update(t_status='Assigned')
                        else:
                            assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                            task.objects.filter(id=taskid).update(t_status='Assigned')

                    else:
                        b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,tl_id=e_id,task_id=t_id)
                        b.save()
                        task.objects.filter(id=taskid).update(t_status='Assigned')
# ===========================================================================================================

                    message = "New Task "+str(j.t_name)+" has been assigned to You."

                    t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                    b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                    b.save()

                    return redirect('/show_tasks')
            
            else:
                for j in task_det:
                    t_id = task.objects.get(id = taskid)
                    e_id=employee.objects.get(id=i.emp_id.id)

# ====================================    Updating Expert ID    ====================================================
                    if assignedTaskTable.objects.filter(task_id=t_id).exists():

                        data_check=assignedTaskTable.objects.filter(task_id=t_id,expert_id__isnull=False)
                        if data_check.exists():
                            assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                            task.objects.filter(id=taskid).update(t_status='Assigned')
                        else:
                            assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                            task.objects.filter(id=taskid).update(t_status='Assigned')
                    
                    else:
                        b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,expert_id=e_id,task_id=t_id)
                        b.save()
                        task.objects.filter(id=taskid).update(t_status='Assigned')
# =================================================================================================================

                    message = "New Task "+str(j.t_name)+" has been assigned to You."

                    t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                    b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                    b.save()

                    return redirect('/show_tasks')
    else:
        details=login.objects.all().filter(username=user_name)
        for m in details:
            
            if((m.role_id.name).lower()=='admin'):
                det=login.objects.all().filter(emp_id=empid)
                for i in det:
                    if((i.role_id.name).lower()=='manager'):
                        for j in task_det:
                            t_id = task.objects.get(id = taskid)
                            e_id=employee.objects.get(id=i.emp_id.id)

# ====================================     Updating manager ID     ==========================================

                            if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                data_check=assignedTaskTable.objects.filter(task_id=t_id,manager_id__isnull=False)
                                if data_check.exists():
                                    assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
                                else:
                                    assignedTaskTable.objects.filter(task_id=t_id).update(manager_id=e_id)
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
                            
                            else:
                                b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,manager_id=e_id,task_id=t_id)
                                b.save()
                                task.objects.filter(id=taskid).update(t_status='Assigned')
# =================================================================================================================

                            message = "New Task "+str(j.t_name)+" has been assigned to You."

                            t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                            b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                            b.save()
                            
                            return redirect('/show_tasks')

                    elif((i.role_id.name).lower()=='tl'):
                        for j in task_det:
                            t_id = task.objects.get(id = taskid)
                            e_id=employee.objects.get(id=i.emp_id.id)

# ====================================    Updating TL ID    =====================================================
                            if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                data_check=assignedTaskTable.objects.filter(task_id=t_id,tl_id__isnull=False)

                                if data_check.exists():
                                    assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
                                else:
                                    assignedTaskTable.objects.filter(task_id=t_id).update(tl_id=e_id,expert_id='')
                                    task.objects.filter(id=taskid).update(t_status='Assigned')

                            else:
                                b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,tl_id=e_id,task_id=t_id)
                                b.save()
                                task.objects.filter(id=taskid).update(t_status='Assigned')
# ===========================================================================================================

                            message = "New Task "+str(j.t_name)+" has been assigned to You."

                            t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                            b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                            b.save()
                            
                            return redirect('/show_tasks')
                    
                    else:
                        for j in task_det:
                            t_id = task.objects.get(id = taskid)
                            e_id=employee.objects.get(id=i.emp_id.id)

# ====================================    Updating Expert ID    ====================================================
                            if assignedTaskTable.objects.filter(task_id=t_id).exists():

                                data_check=assignedTaskTable.objects.filter(task_id=t_id,expert_id__isnull=False)
                                if data_check.exists():
                                    assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
                                else:
                                    assignedTaskTable.objects.filter(task_id=t_id).update(expert_id=e_id)
                                    task.objects.filter(id=taskid).update(t_status='Assigned')
                            
                            else:
                                b=assignedTaskTable(at_name=j.t_name,at_desc=j.t_desc,at_soft=j.t_soft,expert_id=e_id,task_id=t_id)
                                b.save()
                                task.objects.filter(id=taskid).update(t_status='Assigned')
# =================================================================================================================

                            message = "New Task "+str(j.t_name)+" has been assigned to You."

                            t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                            b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                            b.save()

                            return redirect('/show_tasks')


            elif((m.role_id.name).lower()=='manager'):
                det=login.objects.all().filter(emp_id=empid)
                for i in det:
                    if((i.role_id.name).lower()=='tl'):
                        for j in task_det:
                            
                            t_id = task.objects.get(id = taskid)
                            e_id=employee.objects.get(id=i.emp_id.id)
                            m_id=employee.objects.get(id=m.emp_id.id)
                            assignedTaskTable.objects.filter(manager_id=m_id,task_id=t_id).update(tl_id=e_id)

                            message = "New Task "+str(j.t_name)+" has been assigned to You."

                            t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                            b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                            b.save()

                            str1="/show_particular_task/"+str(user_name)
                            return redirect(str1)

                    elif((i.role_id.name).lower()=='expert'):
                        for j in task_det:
                            
                            t_id = task.objects.get(id = taskid)
                            e_id=employee.objects.get(id=i.emp_id.id)
                            m_id=employee.objects.get(id=m.emp_id.id)
                            assignedTaskTable.objects.filter(manager_id=m_id,task_id=t_id).update(expert_id=e_id)

                            message = "New Task "+str(j.t_name)+" has been assigned to You."

                            t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                            b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                            b.save()

                            str1="/show_particular_task/"+str(user_name)
                            return redirect(str1)

            else:
                det=login.objects.all().filter(emp_id=empid)
                for i in det:

                    t_id = task.objects.get(id = taskid)
                    e_id=employee.objects.get(id=i.emp_id.id)
                    m_id=employee.objects.get(id=m.emp_id.id)
                    assignedTaskTable.objects.filter(tl_id=m_id,task_id=t_id).update(expert_id=e_id)

                    message = "New Task "+str(j.t_name)+" has been assigned to You."

                    t=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y:%m:%d %H:%M:%S")
                    b=UserNotifications(from_username=user_name,to_username=i.username,message=message,m_time=t,m_status="unread")
                    b.save()

                    str1="/show_particular_task/"+str(user_name)
                    return redirect(str1)


def assigned_task_details(request,pk):

    task_details = assignedTaskTable.objects.all().filter(id=pk)
    for i in task_details:
        tid = i.task_id.id

    brief_details = filesBrief.objects.all().filter(task_id=tid)
    solution_details = solutionFile.objects.all().filter(task_id=tid)
    user_details=login.objects.all()

    all_comments=comments.objects.filter(from_username=request.user.username,task_id=tid) | comments.objects.filter(to_username=request.user.username,task_id=tid)

    superusers=User.objects.filter(is_superuser=True)

    context={
        'task_details':task_details,
        'brief_details':brief_details,
        'solution_details':solution_details,
        'user_details':user_details,
        'all_comments':all_comments,
        'superusers':superusers,
        }
    return render(request,'assigned_task_details.html',context)

def upload_solution(request,pk,id):
    
    if request.method=="POST":

        uploaded_file = request.FILES.getlist('solution')

        session = boto3.session.Session()
        client = session.client('s3',
                        region_name='ams3',
                        endpoint_url='https://ams3.digitaloceanspaces.com',
                        aws_access_key_id='DO00AL7HLKMKN4ATCBXH',
                        aws_secret_access_key='dAg4Iatdq9g5a9W+7Vhig1jeAOKWbZEY9Zb2kKCOhLY')
    
        for f in uploaded_file:
            fs=FileSystemStorage()
            file_name=fs.save(f.name,f)
            #file_url=fs.url(file_name)

            curr=os.getcwd()
            curr1=os.path.join(curr,file_name)
            #print(curr1)
    
            client.upload_file(curr1 ,  # Path to local file
                                'crmappa',  # Name of Space
                                'crm-spaces-static/media/'+file_name)  # Name for remote file
           
            
            file_url = client.generate_presigned_url(ClientMethod='get_object',
                                    Params={'Bucket': 'crmappa',
                                            'Key': 'crm-spaces-static/media/'+file_name},
                                    ExpiresIn=60*60*24*7)

            fs.delete(file_name)
        
            task_det=assignedTaskTable.objects.all().filter(task_id=pk)
            for i in task_det:
                tid = task.objects.get(id = i.task_id.id)
                desc = i.at_desc
                wc = i.task_id.t_wc
            new_task_sol=solutionFile(sf_name=file_name,sf_desc=desc,sf_wc=wc,sf_link=file_url,task_id=tid ) 
            new_task_sol.save()
       
        str1="/show_employee_details/assigned_task_details/"+str(id)
        return redirect(str1)

def delete_solution(request,pk,id):

    solutionFile.objects.filter(id=pk).delete()
    str1="/show_employee_details/assigned_task_details/"+str(id)
    return redirect(str1)

def settings(request):

    return render(request,'settings.html')

def roles_permissions(request):

    groups=Group.objects.all()
    context={
        'groups':groups,
            }
    return render(request,'roles_permissions.html',context)


def create_role(request):
    if request.method == "POST":
        role_name = request.POST['role_name']
        sel_perm = request.POST.getlist('checks')
        b = role(role_name = role_name)
        b.save()
        rid = role.objects.get(role_name=role_name)
        
        str=''
        for i in sel_perm:
            str=str+"'"+i+"'\n"
        b=permission(permission_name=str,role_id=rid)
        b.save()

        return redirect('roles_permissions')

 
def show_edit_role(request,pk):
    gl_roleid.clear()
    gl_roleid.append(pk)
    Create_Client   = " "
    Update_Client = " "
    View_Client = " "
    Create_Task = " "
    Update_Task = " "
    View_Tasks = " "
    Upload_Briefs = " "
    Upload_Solution = " "
    Delete_Task = " "
    View_Payment = " "
    Edit_Payment = " "
    Create_Employee = " "
    Edit_Employee = " "
    Delete_Employee = " "
    View_Employee = " "
    Assign_Task = " "
    Create_User = " "
    Delete_User = " "
    View_Users = " "
    Create_Role = " "
    Delete_Role = " "
    Edit_Roles = " "
    View_Roles = " "

    perm_det = permission.objects.all().filter(role_id = pk )
    for i in perm_det :
        str1 = (i.permission_name).replace(",","")
        if "Create Client" in str1:
            Create_Client='checked'
        if "Update Client" in str1:
            Update_Client='checked'
        if "View Client" in str1:
            View_Client ='checked'
        if "Create Task" in str1:
            Create_Task='checked'
        if "Update Task" in str1:
            Update_Task='checked'
        if "View Tasks" in str1:
            View_Tasks='checked'
        if "Upload Briefs" in str1:
            Upload_Briefs='checked'
        if "Upload Solution" in str1:
            Upload_Solution='checked'
        if "Delete Task" in str1:
            Delete_Task='checked'
        if "View Payment" in str1:
            View_Payment='checked'
        if "Edit Payment" in str1:
            Edit_Payment='checked'
        if "Create Employee" in str1:
            Create_Employee='checked'
        if "Edit Employee" in str1:
            Edit_Employee='checked'
        if "Delete Employee" in str1:
            Delete_Employee='checked'
        if "View Employee" in str1:
            View_Employee='checked'
        if "Assign Task" in str1:
            Assign_Task='checked'
        if "Create User" in str1:
            Create_User='checked'
        if "Delete User" in str1:
            Delete_User='checked'
        if "View Users" in str1:
            View_Users='checked'
        if "Create Role" in str1:
            Create_Role='checked'
        if "Delete Role" in str1:
            Delete_Role='checked'
        if "Edit Roles" in str1:
            Edit_Roles='checked'
        if "View Roles" in str1:
            View_Roles='checked'

    context ={
        'perm':perm_det,
         'a' :  Create_Client   ,
         'b' :  Update_Client ,
         'c' :  View_Client ,
         'd' :  Create_Task ,
         'e' :  Update_Task ,
         'f' :  View_Tasks ,
         'g' :  Upload_Briefs ,
         'h' :  Upload_Solution ,
         'i':   Delete_Task ,
         'j' :  View_Payment ,
         'k' :  Edit_Payment ,
        'l'  :  Create_Employee ,
         'm' :  Edit_Employee ,
         'n' :  Delete_Employee ,
        'o' :   View_Employee ,
         'p':   Assign_Task ,
         'q':   Create_User ,
          'r' : Delete_User ,
          's' : View_Users ,
          't' : Create_Role ,
         'u'  : Delete_Role ,
         'v' :  Edit_Roles ,
         'w' :  View_Roles ,
                
    }
    return render( request,'show_edit_role.html',context)

def updated_role(request):
    if request.method == "POST":
    
        sel_perm = request.POST.getlist('checks')

        
        str=''
        for i in sel_perm:
            str=str+"'"+i+"'\n"
        
        permission.objects.filter(role_id=gl_roleid[0]).update(permission_name=str)
        return redirect('roles_permissions')

def delete_role(request,pk):
    role.objects.filter(id=pk).delete()
    return redirect('roles_permissions')
    
def user_details(request):

    entries = login.objects.all()
    roles = Group.objects.all()
    final=employee.objects.all()
    
    context={
        'entries':entries,
        'final':final,
        'roles':roles,
        
    }
    return render(request,'user_details.html',context)

def create_user(request):
    if request.method == "POST":

        emp_id = request.POST['e_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role_id = request.POST['role_id']
        users =[]
        user_names = login.objects.all()

        user_email = employee.objects.all().filter(id = emp_id)
        
        for i in user_email:
            u_email = i.e_email

        if password1 == password2:
            if User.objects.filter(username = username).exists():
                messages.info(request,'Username already exists')
                return redirect('user_details')
                
            else:
                user1 = User.objects.create_user(username = username,email=u_email,password = password1) 
                user1.save()

                group = Group.objects.get(name=role_id)
                group.user_set.add(user1)

                emp_id1 = employee.objects.get(id = emp_id)
                role_id1=Group.objects.get(name=role_id)

                c = login(username = username,password = password1,emp_id = emp_id1,role_id = role_id1)
                c.save()

                employee.objects.filter(id=emp_id).update(role_id=role_id1)
            
                return redirect('user_details')
        else:
            messages.info(request,"Password dosen't match")
            return redirect('user_details')


def update_user(request,pk):

    entries = login.objects.all().filter(id = pk)
    groups=Group.objects.all()
    context={
        'entries':entries,
        'groups':groups
    }
    return render(request,'update_user.html', context)


def updated_user(request,pk):
    if request.method =="POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role_name=request.POST['role_name']
        user_name = login.objects.all().filter(id = pk)
        for i in user_name:
            if password1 == password2 :
                user_update = User.objects.get(username = i.username)
                user_update.set_password(password1)
                user_update.save()

                if(int(role_name)==int(i.role_id.id)):
                    login.objects.filter(id = pk).update(password = password1)
                else:
                    role=Group.objects.get(id=role_name)
                    login.objects.filter(id = pk).update(password = password1, role_id=role)
                    employee.objects.filter(id=i.emp_id.id).update(role_id=role)
                    grp_name=Group.objects.all().filter(id=role_name)
                    user_det=User.objects.get(username=i.username)
                    for j in grp_name:
                        grp=Group.objects.get(name=j.name)
                        user_det.groups.clear()
                        grp.user_set.add(user_det)

                return redirect('user_details')

def delete_user(request,pk):

    user_name = login.objects.all().filter(id = pk)
    for i in user_name:
        User.objects.filter(username = i.username).delete()
        login.objects.filter(id = pk).delete()
        return redirect('user_details')

def task_complete(request,pk,user_name,id):

    log_det=login.objects.all().filter(username=user_name)
    for i in log_det:

        if((i.role_id.name).lower()=='manager'):
            task.objects.filter(id=pk).update(t_status='Delivered')
            str1='/show_employee_details/assigned_task_details/'+str(id)
            return redirect(str1)

        if((i.role_id.name).lower()=='tl'):
            task.objects.filter(id=pk).update(t_status='Completed')
            str1='/show_employee_details/assigned_task_details/'+str(id)
            return redirect(str1)

        else:
            task.objects.filter(id=pk).update(t_status='Quality Check')
            str1='/show_employee_details/assigned_task_details/'+str(id)
            return redirect(str1)

def show_particular_task(request,pk):

    if request.method=='GET':
        employee_id=login.objects.all().filter(username=pk)
	
        for i in employee_id:
            
            group_name=Group.objects.all().filter(id=i.role_id.id)
            for j in group_name:
                
                if(j.name.lower()=='manager'):
                    tasks=assignedTaskTable.objects.all().filter(manager_id=i.emp_id.id)
                    
                    tl_details=User.objects.filter(groups__name='TL')
                    expert_details=User.objects.filter(groups__name='Expert')
                    
                    tl_list=[]
                    expert_list=[]
                    
                    for m in tl_details:
                        tl_det=login.objects.all().filter(username=m.username)
                        tl_list.append(tl_det)

                    for n in expert_details:
                        expert_det=login.objects.all().filter(username=n.username)
                        expert_list.append(expert_det)

                    context={
                    'employee_task_details':tasks,
                    'tl_list':tl_list,
                    'expert_list':expert_list,
                    'admin':'Admin',
                    'val1':'True',
                    }
                    return render(request,'show_tasks.html',context) 
                    
                elif(j.name.lower()=='tl'):
                    tasks=assignedTaskTable.objects.all().filter(tl_id=i.emp_id.id)

                    group_members=grouptable.objects.all().filter(tl_emp_id=i.emp_id.id)

                    grp_mem_list=[]

                    for i in group_members:
                        grp_mem_list.append(login.objects.all().filter(emp_id=i.members_emp_id.id))

                    context={
                    'employee_task_details':tasks,
                    'grp_mem_list':grp_mem_list,
                    'val2':'True',
                    }
                    return render(request,'show_tasks.html',context)
                else:
                    tasks=assignedTaskTable.objects.all().filter(expert_id=i.emp_id.id)

                    context={
                    'employee_task_details':tasks,
                    'val3':'True'
                    }
                    return render(request,'show_tasks.html',context) 

    else:
        return render(request,'show_tasks.html')

def upload_new_solution(request,pk):

    if request.method=="POST":

        uploaded_file = request.FILES.getlist('solution')

        session = boto3.session.Session()
        client = session.client('s3',
                        region_name='ams3',
                        endpoint_url='https://ams3.digitaloceanspaces.com',
                        aws_access_key_id='DO00AL7HLKMKN4ATCBXH',
                        aws_secret_access_key='dAg4Iatdq9g5a9W+7Vhig1jeAOKWbZEY9Zb2kKCOhLY')
        
        for f in uploaded_file:
            fs=FileSystemStorage()
            file_name=fs.save(f.name,f)
            #file_url=fs.url(file_name)

            curr=os.getcwd()
            curr1=os.path.join(curr,file_name)
            #print(curr1)
    
            client.upload_file(curr1 ,  # Path to local file
                                'crmappa',  # Name of Space
                                'crm-spaces-static/media/'+file_name)  # Name for remote file
           
            
            file_url = client.generate_presigned_url(ClientMethod='get_object',
                                    Params={'Bucket': 'crmappa',
                                            'Key': 'crm-spaces-static/media/'+file_name},
                                    ExpiresIn=60*60*24*7)

            fs.delete(file_name)

            task_det=task.objects.all().filter(id=pk)
            for i in task_det:
                tid = task.objects.get(id = pk)
                desc = i.t_desc
                wc = i.t_wc
                new_task_sol=solutionFile(sf_name=file_name,sf_desc=desc,sf_wc=wc,sf_link=file_url,task_id=tid ) 
                new_task_sol.save()

        str1="/show_task_details/"+str(pk)
        return redirect(str1)

def delete_new_solution(request,pk,id):

    solutionFile.objects.filter(id=pk).delete()
    str1="/show_task_details/"+str(id)
    return redirect(str1)

def create_role_group(request):
    
    return redirect('/admin/auth/group')

def maps(request):
    return render(request,'maps.html')

def profile(request,user_name):
    
    if(User.objects.get(username=user_name).is_superuser):
        
        context = {
                    'me' : "Marketing Executive",
                    'manager' : "Manager",
                    'tl' :"TL",
                    'expert' : "Expert",
                }
        return render(request,'profiles.html',context)
    else:
        details=login.objects.all().filter(username=user_name)
        
        for i in details:
            if((i.role_id.name).lower()=='admin'):
                context = {
                    'me' : "Marketing Executive",
                    'manager' : "Manager",
                    'tl' :"TL",
                    'expert' : "Expert",
                }
                return render(request,'profiles.html',context)
            else:
                for i in details:
                    user_profile_id = i.emp_id.id

                    user_pro_details = employee.objects.all().filter(id = user_profile_id)
                    user_att_details = attendanceTable.objects.all().filter(att_employee_id_id = user_profile_id)
                    
                    context = {
                        'user_pro_details':user_pro_details,
                        'user_log_details' : details,
                        'user_att_details' : user_att_details,
                        
                    }
                    
                return render(request,'user_profile.html',context)
                

def profile_admin(request,pk):
    log_details=login.objects.all().filter(emp_id=pk)
    print(log_details)
    for i in log_details:
        print(i.username)
        str1=str("/profile")+str("/")+str(i.username)
        return redirect(str1)
    

def show_cat(request,role_names):
    
    role_details = Group.objects.all().filter(name = str(role_names))
    
    for i in role_details:
        emp_details_role = employee.objects.all().filter(role_id = i.id)

    context = {
        'details' : emp_details_role
    }
    return render(request, 'show_cat_profile.html',context)


def show_groups(request,user_name):

    if(User.objects.get(username=user_name).is_superuser):
        print(user_name)
        print("=========================1")
        group=Group.objects.all().filter(name='TL')
        print(group)
        mem_group=Group.objects.all().filter(name='Expert')
        for i in group:
            print(user_name)
            print("=========================2")
            for j in mem_group:
                print(user_name)
                print("=========================3")
                users=login.objects.all().filter(role_id=i.id)
                members=login.objects.all().filter(role_id=j.id)
                
                g=grouptable.objects.all()
                mem_ids=[i.emp_id.id for i in members ]
                mem_grp_ids=[i.members_emp_id.id for i in g]

                members_list=[]

                if(len(mem_ids)>len(mem_grp_ids)):
                    for i in list(set(mem_ids)-set(mem_grp_ids)):
                        members_list.append(employee.objects.all().filter(id=i))
                else:
                    for i in list(set(mem_grp_ids)-set(mem_ids)):
                        members_list.append(employee.objects.all().filter(id=i))

                context={
                    'users':users,
                    'members':members,
                    'members_list':members_list,
                }
                return render(request,'groups.html',context)
    else:
        details=login.objects.all().filter(username=user_name)
        for i in details:
            if((i.role_id.name).lower()=='admin' or (i.role_id.name).lower()=='manager' or (i.role_id.name).lower()=='hr' or (i.role_id.name).lower()=='sr'):
                group=Group.objects.all().filter(name='TL')
                mem_group=Group.objects.all().filter(name='Expert')
                for i in group:
                    for j in mem_group:
                        users=login.objects.all().filter(role_id=i.id)
                        members=login.objects.all().filter(role_id=j.id)
                        
                        context={
                            'users':users,
                            'members':members,
                        }
                        return render(request,'groups.html',context)
            else:
                return render(request,'specific_group.html')

def create_group(request,user_name):

    if request.method=='POST':
        team_lead=request.POST['tl_name']
        members=request.POST.getlist('member_checks')
        
        tl_id=employee.objects.get(id=team_lead)
        for i in members:
            mem_id=employee.objects.get(id=i)
            b=grouptable(tl_emp_id=tl_id,members_emp_id=mem_id)
            b.save()

        str1='/show_groups/'+str(user_name)
        return redirect(str1)
        
def show_particular_group(request,user_name,pk):

    group_details=grouptable.objects.all().filter(tl_emp_id=pk)
    em_tl=employee.objects.all().filter(id=pk)
    context={
        'group_details':group_details,
        'em_tl':em_tl,
    }
    return render(request,'show_particular_group.html',context)

def remove_member(request,user_name,tl_id,mem_id):

    grouptable.objects.get(members_emp_id=mem_id).delete()
    str1="/show_particular_group/"+str(user_name)+"/"+str(tl_id)
    return redirect(str1)

def show_tl_group(request,user_name):
    
    empid=login.objects.all().filter(username=user_name)
    for i in empid:
        emp=i.emp_id.id
        
        str1="/show_particular_group/"+str(user_name)+str("/")+str(emp)
        return redirect(str1)

def create_comment(request,user_name,pk,task_name):
    if request.method=='POST':

        desc=request.POST['comment_desc']
        u_name=request.POST['comment_to_emp']
        
        task_det=task.objects.get(id=pk)
        
        b=comments(from_username=user_name,to_username=u_name,task_id=task_det,task_name=task_name,message=desc)
        b.save()

        str1="/show_task_details/"+str(pk)
        return redirect(str1)

def assigned_comment(request,user_name,pk,task_name):
    if request.method=='POST':

        desc=request.POST['comment_desc']
        u_name=request.POST['comment_to_emp']

        task_det=assignedTaskTable.objects.filter(id=pk)
        for i in task_det:
            tid=i.task_id.pk
            task_id=task.objects.get(id=tid)
        
        b=comments(from_username=user_name,to_username=u_name,task_id=task_id,task_name=task_name,message=desc)
        b.save()

        str1="/show_employee_details/assigned_task_details/"+str(pk)
        return redirect(str1)

def bulk_task_creation(request):

    if request.method=='POST':

        bulk_file=request.FILES.getlist('bulk_tasks')

        for f in bulk_file:
            fs=FileSystemStorage()
            file_name=fs.save(f.name,f)
            file_url=fs.url(file_name)

            curr_dir=os.getcwd()
            file_url=file_url.replace("/","\\")
            file_url=file_url.replace("\\","",1)
            curr_file=os.path.join(curr_dir,file_url)

            df=pd.read_excel(curr_file)
            
            for i in range(0,len(df.index)):
                task_name=df['Task_name'].iloc[i]
                task_desc=df['Task_Description'].iloc[i]
                task_soft=df['Task_Soft_deadline'].iloc[i]
                task_hard=df['Task_Hard_deadline'].iloc[i]
                task_wc=df['Task_WordCount'].iloc[i]
                task_amt=df['Task_Amount'].iloc[i]
                task_cur=df['Currency'].iloc[i]
                task_clientid=df['Client_id'].iloc[i]
                task_amt_paid=df['Amount_Paid'].iloc[i]

                task_due_amt=df['Task_Amount'].iloc[i]-df['Amount_Paid'].iloc[i]

                new_task = task(t_name=task_name,t_soft=task_soft,t_hard=task_hard,t_amount=task_amt,t_currency=task_cur ,t_wc = task_wc,t_status="Unassigned", t_desc = task_desc, client_id_id=task_clientid)
                new_task.save()

                all_ids=task.objects.values_list('id',flat=True)
                all=list(int(x) for x in all_ids)
                max_val=max(all)

                task_ids=task.objects.get(id=max_val)

                today = date.today()
                now = datetime.now()
                current_time =  now.strftime("%H:%M:%S")
                new_payment=payment(due_amount=task_due_amt,p_status="Partial",task_id=task_ids,p_date=today,p_time=current_time)
                new_payment.save()

                fs.delete(file_name)                

        return redirect('/show_tasks')

    else:
        return redirect('/show_tasks')

def show_attendance(request):

    att_details=attendanceTable.objects.all()
    context={'details':att_details}

    return render(request,'show_attendance.html',context)

def revoke_tasks(request,user_name):

    taskid=request.POST['task_name']

    if(User.objects.get(username=user_name).is_superuser):

        task_det=task.objects.filter(pk=taskid)
        for i in task_det:
            status=i.t_status
        if status == "Unassigned":
            pass
        else:
            assignedTaskTable.objects.filter(task_id=taskid).update(manager_id="",tl_id="",expert_id="")
            task_det=task.objects.filter(pk=taskid).update(t_status="Unassigned")

        return redirect('/show_tasks')

    else:
        details=login.objects.all().filter(username=user_name)
        for m in details:
            
            if((m.role_id.name).lower()=='admin'):
                task_det=task.objects.filter(pk=taskid)
                for i in task_det:
                    status=i.t_status
                if status == "Unassigned":
                    pass
                else:
                    assignedTaskTable.objects.filter(task_id=taskid).update(manager_id="",tl_id="",expert_id="")
                    task_det=task.objects.filter(pk=taskid).update(t_status="Unassigned")

                return redirect('/show_tasks')

            elif((m.role_id.name).lower()=='manager'):

                assignedTaskTable.objects.filter(task_id=taskid).update(tl_id="",expert_id="")
                str1="/show_particular_task/"+str(user_name)
                return redirect(str1)

            elif((m.role_id.name).lower()=='tl'):

                assignedTaskTable.objects.filter(task_id=taskid).update(expert_id="")
                str1="/show_particular_task/"+str(user_name)
                return redirect(str1)
        else:
            return redirect('/show_tasks')

def show_notifications(request):

    user_name=request.user.username
    all_users=UserNotifications.objects.filter(to_username=user_name,m_status='unread').order_by('-id')

    all_users = serializers.serialize("json", all_users)

    stud_obj = json.loads(all_users)

    counts = UserNotifications.objects.filter(to_username=user_name,m_status='unread').count()

    response = {
        'all_users':stud_obj,
        'counts':counts,
    }
    return JsonResponse(response)
    

def mark_read(request,note_id):
    
    UserNotifications.objects.filter(id=note_id).update(m_status="read")

    response = {
        'marked':True
    }
    return JsonResponse(response)
