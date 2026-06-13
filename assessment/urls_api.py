from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views_api

router = DefaultRouter()
router.register(r'employees', views_api.EmployeeViewSet, basename='api_employees')
router.register(r'questions', views_api.QuestionViewSet, basename='api_questions')
router.register(r'tasks', views_api.TaskViewSet, basename='api_tasks')
router.register(r'results', views_api.ResultViewSet, basename='api_results')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', views_api.me_view, name='api_me'),
    path('dashboard/', views_api.dashboard_stats, name='api_dashboard'),
    path('', include(router.urls)),
]
