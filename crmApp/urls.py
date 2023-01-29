from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.signin,name='signin'),
    path('index',views.index,name='index'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('maps',views.maps,name='maps'),
    path('profile/<str:user_name>',views.profile,name='profile'),
    path('show_clients_cards',views.show_clients_cards,name='show_clients_cards'),    
    path('show_clients',views.show_clients,name='show_clients'),
    path('create_client',views.create_client,name='create_client'),
    path('logout',views.logout,name='logout'),
    path('show_tasks',views.show_tasks,name='show_tasks'),
    path('show_client_details/<int:pk>',views.show_client_details,name='show_client_details'),
    path('create_task',views.create_task,name='create_task'),
    path('show_payments',views.show_payments,name='show_payments'),
    path('update_client/<int:pk>',views.update_client,name='update_client'),
    path('update_client/updated/<int:pk>',views.updated,name='updated'),
    path('update_task/<int:pk>',views.update_task,name='update_task'),
    path('update_task/updated_task/<int:pk>',views.updated_task,name='updated_task'),
    path('update_payment/<int:pk>',views.update_payment,name='update_payment'),
    path('update_payment/updated_payment/<int:pk>',views.updated_payment,name='updated_payment'),
    path('show_task_details/<int:pk>',views.show_task_details,name='show_task_details'),
    path('show_task_details/upload_new_brief/<int:pk>/<int:id>',views.upload_new_brief,name='upload_new_brief'),
    path('show_task_details/delete_brief/<int:pk>/<int:id>',views.delete_brief,name='delete_brief'),
    path('delete_task/<int:pk>',views.delete_task,name='delete_task'),
    path('show_employee_cards',views.show_employee_cards,name='show_employee_cards'), 
    path('show_employees',views.show_employees,name='show_employees'),
    path('create_employee',views.create_employee,name='create_employee'),
    path('show_employee_details/<int:pk>',views.show_employee_details,name='show_employee_details'),
    path('update_employee/<int:pk>',views.update_employee,name='update_employee'),
    path('update_employee/updated_employee/<int:pk>',views.updated_employee,name='updated_employee'),
    path('delete_employee/<int:pk>',views.delete_employee,name='delete_employee'),
    path('assign_task/<str:user_name>',views.assign_task,name='assign_task'),
    path('show_employee_details/assigned_task_details/<int:pk>',views.assigned_task_details,name='assigned_task_details'),
    path('show_employee_details/assigned_task_details/upload_solution/<int:pk>/<int:id>',views.upload_solution,name='upload_solution'),
    path('show_employee_details/assigned_task_details/delete_solution/<int:pk>/<int:id>',views.delete_solution,name='delete_solution'),
    path('settings',views.settings,name='settings'),
    path('pages-profile/<int:pk>',views.update_user,name='update_user'),    
    path('roles_permissions',views.roles_permissions,name='roles_permissions'),    
    path('create_role',views.create_role,name='create_role'),
    path('show_edit_role/<int:pk>',views.show_edit_role,name='show_edit_role'),
    path('show_edit_role/updated_role',views.updated_role,name='updated_role'),
    path('delete_role/<int:pk>',views.delete_role,name='delete_role'),
    path('user_details',views.user_details,name='user_details'),
    path('create_user',views.create_user,name='create_user'),
    path('update_user/<int:pk>',views.update_user,name='update_user'),
    path('update_user/updated_user/<int:pk>',views.updated_user,name='updated_user'),
    path('delete_user/<int:pk>',views.delete_user,name='delete_user'),
    path('show_employee_details/assigned_task_details/task_complete/<int:pk>/<str:user_name>/<int:id>',views.task_complete,name='task_complete'),
    path('show_particular_task/<str:pk>',views.show_particular_task,name='show_particular_task'),
    path('show_task_details/upload_new_solution/<int:pk>',views.upload_new_solution,name='upload_new_solution'),
    path('show_task_details/delete_new_solution/<int:pk>/<int:id>',views.delete_new_solution,name='delete_new_solution'),
    path('create_role_group',views.create_role_group,name='create_role_group'),
    path('show_groups/<str:user_name>',views.show_groups,name='show_groups'),
    path('create_group/<str:user_name>',views.create_group,name='create_group'),
    path('show_particular_group/<str:user_name>/<int:pk>',views.show_particular_group,name='show_particular_group'),
    path('remove_member/<str:user_name>/<int:tl_id>/<int:mem_id>',views.remove_member,name='remove_member'),
    path('show_tl_group/<str:user_name>',views.show_tl_group,name='show_tl_group'),
    path('assign_particular_task/<str:user_name>',views.assign_particular_task,name='assign_particular_task'),
    path('create_comment/<str:user_name>/<int:pk>/<str:task_name>',views.create_comment,name='create_comment'),
    path('assigned_comment/<str:user_name>/<int:pk>/<str:task_name>',views.assigned_comment,name='assigned_comment'),
    path('bulk_task_creation',views.bulk_task_creation,name='bulk_task_creation'),
    path('mark_attendance',views.mark_attendance,name='mark_attendance'),
    path('show_attendance',views.show_attendance,name='show_attendance'),
    path('revoke_tasks/<str:user_name>',views.revoke_tasks,name='revoke_tasks'),
    path('show_notifications',views.show_notifications,name='show_notifications'),
    path('mark_read/<int:note_id>',views.mark_read,name='mark_read'),
    path('show_cat/<str:role_names>',views.show_cat,name='show_cat'),
    path('profile_admin/<int:pk>',views.profile_admin,name='profile_admin'),
    path('pay', views.pay, name='pay'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)