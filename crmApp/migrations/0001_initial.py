# Generated by Django 3.0.5 on 2021-06-22 04:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_name', models.CharField(max_length=20, null=True)),
                ('c_num', models.CharField(max_length=30, null=True)),
                ('c_email', models.CharField(max_length=50, null=True)),
                ('c_address', models.CharField(max_length=100, null=True)),
                ('c_university', models.CharField(max_length=50, null=True)),
                ('c_desc', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('e_name', models.CharField(max_length=20, null=True)),
                ('e_num', models.CharField(max_length=30, null=True)),
                ('e_email', models.CharField(max_length=50, null=True)),
                ('e_address', models.CharField(max_length=100, null=True)),
                ('e_account_no', models.IntegerField()),
                ('e_ifsc', models.CharField(max_length=20, null=True)),
                ('role_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('t_desc', models.CharField(max_length=100, null=True)),
                ('t_name', models.CharField(max_length=20)),
                ('t_soft', models.DateField(null=True)),
                ('t_hard', models.DateField()),
                ('t_wc', models.IntegerField()),
                ('t_amount', models.IntegerField()),
                ('t_currency', models.CharField(max_length=40, null=True)),
                ('t_status', models.CharField(max_length=20, null=True)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.client')),
            ],
        ),
        migrations.CreateModel(
            name='solutionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sf_name', models.CharField(max_length=20)),
                ('sf_desc', models.CharField(max_length=100)),
                ('sf_wc', models.IntegerField()),
                ('sf_link', models.CharField(max_length=100)),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.task')),
            ],
        ),
        migrations.CreateModel(
            name='permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_name', models.CharField(max_length=20)),
                ('role_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_amount', models.CharField(max_length=10, null=True)),
                ('p_status', models.CharField(max_length=20, null=True)),
                ('p_date', models.DateField(null=True)),
                ('p_time', models.TimeField(null=True)),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.task')),
            ],
        ),
        migrations.CreateModel(
            name='login',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=20)),
                ('emp_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.employee')),
                ('role_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='grouptable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('members_emp_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_ids', to='crmApp.employee')),
                ('tl_emp_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_lead_id', to='crmApp.employee')),
            ],
        ),
        migrations.CreateModel(
            name='filesBrief',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(max_length=20)),
                ('f_desc', models.CharField(max_length=100)),
                ('f_link', models.FileField(upload_to='upload/documents/')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.task')),
            ],
        ),
        migrations.CreateModel(
            name='employeeFileBrief',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('efb_name', models.CharField(max_length=20)),
                ('efb_desc', models.CharField(max_length=100)),
                ('efb_link', models.FileField(upload_to='upload/documents/')),
                ('emp_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.employee')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.task')),
            ],
        ),
        migrations.CreateModel(
            name='deletedEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('de_name', models.CharField(max_length=20, null=True)),
                ('de_num', models.IntegerField()),
                ('de_email', models.CharField(max_length=50, null=True)),
                ('de_address', models.CharField(max_length=100, null=True)),
                ('de_account_no', models.IntegerField()),
                ('de_ifsc', models.CharField(max_length=20, null=True)),
                ('tasks', models.IntegerField()),
                ('role_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='cancelledTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ctask_desc', models.CharField(max_length=100)),
                ('ctask_name', models.CharField(max_length=50)),
                ('ct_hard', models.DateField()),
                ('ct_wc', models.IntegerField()),
                ('ct_amount', models.IntegerField()),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='crmApp.client')),
            ],
        ),
        migrations.CreateModel(
            name='cancelledBrief',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cbf_name', models.CharField(max_length=20)),
                ('cbf_desc', models.CharField(max_length=100)),
                ('cbf_link', models.CharField(max_length=100)),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='crmApp.task')),
            ],
        ),
        migrations.CreateModel(
            name='attendanceTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('att_employee_name', models.CharField(max_length=50)),
                ('att_date', models.DateField(null=True)),
                ('att_time', models.TimeField(null=True)),
                ('att_status', models.CharField(max_length=10)),
                ('att_employee_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='crmApp.employee')),
            ],
        ),
        migrations.CreateModel(
            name='assignedTaskTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at_desc', models.CharField(max_length=100, null=True)),
                ('at_name', models.CharField(max_length=20)),
                ('at_soft', models.DateField(null=True)),
                ('expert_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='expert_id', to='crmApp.employee')),
                ('manager_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_id', to='crmApp.employee')),
                ('task_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crmApp.task')),
                ('tl_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tl_id', to='crmApp.employee')),
            ],
        ),
    ]
