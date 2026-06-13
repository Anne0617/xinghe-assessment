from django.urls import path
from . import views
from . import views_employee as ev

app_name = 'assessment'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    # 员工测评入口
    path('assessment/', ev.EmployeeAccessView.as_view(), name='employee_access'),
    path('assessment/take/<str:code>/', ev.EmployeeTakeView.as_view(), name='employee_take'),
    path('assessment/submit/<str:code>/', ev.EmployeeSubmitView.as_view(), name='employee_submit'),
    path('assessment/thanks/', ev.EmployeeThanksView.as_view(), name='employee_thanks'),
    path('assessment/result/<str:code>/', ev.EmployeeResultView.as_view(), name='employee_result'),
]

