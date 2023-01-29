from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class role(models.Model):
    role_name=models.CharField(null = True,max_length=20)


class login(models.Model):
    username= models.CharField(null=False,max_length= 20)
    password = models.CharField(null=False, max_length=20)
    role_id=models.ForeignKey(Group,on_delete=models.CASCADE)
    emp_id = models.ForeignKey("employee",on_delete=models.CASCADE)
    
class employee(models.Model):
    e_name=models.CharField(null=True,max_length=20)
    e_num=models.CharField(null=True,max_length=30)
    e_email=models.CharField(null=True,max_length=50)
    e_address=models.CharField(null=True,max_length=100)
    e_account_no=models.IntegerField()
    e_ifsc= models.CharField(null=True,max_length=20)
    role_id=models.ForeignKey(Group,on_delete=models.CASCADE)


class permission(models.Model):
    permission_name=models.CharField(max_length=20)
    role_id=models.ForeignKey(Group,on_delete=models.CASCADE)

class client(models.Model):
    c_name=models.CharField(null=True,max_length=20)
    c_num=models.CharField(null=True,max_length=30)
    c_email=models.CharField(null=True,max_length=50)
    c_university=models.CharField(null=True,max_length=100)
    c_created_by = models.CharField(max_length=30)

class task(models.Model):
    t_desc=models.CharField(null=True, max_length=100)
    t_name=models.CharField(null=False, max_length=20)
    t_soft=models.DateField(null=True,blank=False)
    t_hard=models.DateField(null=False,blank=False)
    t_wc = models.IntegerField()
    t_amount=models.IntegerField()
    t_currency=models.CharField(null=True,max_length=40)
    t_status = models.CharField(null=True,max_length = 20)
    client_id=models.ForeignKey("client",on_delete=models.CASCADE)
    t_created_by = models.CharField(max_length=30)

class cancelledTask(models.Model):
    ctask_desc=models.CharField(null=False,max_length=100)
    ctask_name = models.CharField(null=False,max_length=50)
    ct_hard=models.DateField(null=False,blank=False)
    ct_wc = models.IntegerField()
    ct_amount = models.IntegerField()
    client_id=models.ForeignKey("client",on_delete=models.DO_NOTHING)

class filesBrief(models.Model):
    f_name = models.CharField(null=False, max_length=20)
    f_desc = models.CharField(null=False,max_length=100)
    f_link = models.FileField(upload_to='upload/documents/')
    task_id=models.ForeignKey("task",on_delete=models.CASCADE)

class solutionFile(models.Model):
    sf_name = models.CharField(null=False, max_length=20)
    sf_desc = models.CharField(null=False, max_length=100)
    sf_wc =   models.IntegerField()
    sf_link = models.CharField(null=False,max_length=100)
    task_id=models.ForeignKey("task",on_delete=models.CASCADE)
   


class payment(models.Model):
    due_amount=models.CharField(null = True , max_length = 10)
    p_status=models.CharField(null=True,max_length=20)
    p_date=models.DateField(null=True,blank=False)
    p_time = models.TimeField(null=True,blank=False)
    task_id=models.ForeignKey("task",on_delete=models.CASCADE)
    p_created_by = models.CharField(max_length=30)


class cancelledBrief(models.Model):
    cbf_name = models.CharField(null=False, max_length=20)
    cbf_desc = models.CharField(null=False,max_length=100)
    cbf_link = models.CharField(null=False,max_length=100)
    task_id=models.ForeignKey("task",on_delete=models.DO_NOTHING)

class assignedTaskTable(models.Model):
    at_desc=models.CharField(null=True, max_length=100)
    at_name=models.CharField(null=False, max_length=20)
    at_soft=models.DateField(null=True,blank=False)
    task_id=models.ForeignKey("task",on_delete=models.CASCADE)
    manager_id=models.ForeignKey("employee",on_delete=models.DO_NOTHING,related_name="manager_id")
    tl_id=models.ForeignKey("employee",on_delete=models.DO_NOTHING,related_name="tl_id")
    expert_id=models.ForeignKey("employee",on_delete=models.DO_NOTHING,related_name="expert_id")

class employeeFileBrief(models.Model):
    efb_name = models.CharField(null=False, max_length=20)
    efb_desc = models.CharField(null=False,max_length=100)
    efb_link = models.FileField(upload_to='upload/documents/')
    task_id=models.ForeignKey("task",on_delete=models.CASCADE)
    emp_id = models.ForeignKey("employee",on_delete=models.CASCADE)

class deletedEmployee(models.Model):
    de_name=models.CharField(null=True,max_length=20)
    de_num=models.IntegerField()
    de_email=models.CharField(null=True,max_length=50)
    de_address=models.CharField(null=True,max_length=100)
    de_account_no=models.IntegerField()
    de_ifsc= models.CharField(null=True,max_length=20)
    tasks = models.IntegerField()
    role_id=models.ForeignKey(Group,on_delete=models.CASCADE)


class grouptable(models.Model):
    tl_emp_id=models.ForeignKey("employee",on_delete=models.CASCADE,related_name="team_lead_id")
    members_emp_id=models.ForeignKey("employee",on_delete=models.CASCADE,related_name="member_ids")

class attendanceTable(models.Model):
    att_employee_id=models.ForeignKey("employee",on_delete=models.DO_NOTHING)
    att_employee_name=models.CharField(max_length=50)
    att_date=models.DateField(null=True)
    att_time=models.TimeField(null=True)
    att_status=models.CharField(max_length=10)


class comments(models.Model):
    from_username=models.CharField(max_length=30,null=True)
    to_username=models.CharField(max_length=30,null=True)
    task_id=models.ForeignKey("task",on_delete=models.CASCADE,null=True)
    task_name=models.CharField(max_length=30,null=True)
    message=models.CharField(max_length=255,null=True)

class UserNotifications(models.Model):
    from_username=models.CharField(max_length=30,null=True)
    to_username=models.CharField(max_length=30,null=True)
    message=models.CharField(max_length=100,null=True)
    m_time=models.CharField(max_length=30,null=True)
    m_status=models.CharField(max_length=30,null=True)
