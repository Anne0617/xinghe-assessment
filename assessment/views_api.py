from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Employee, Question, AssessmentTask, AssessmentResult
from .serializers import UserSerializer, EmployeeSerializer, QuestionSerializer, TaskSerializer, ResultSerializer
from accounts.models import User

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    user = request.user
    q = Q()
    if user.is_hr_admin and user.branch:
        q = Q(branch=user.branch)
    employees = Employee.objects.filter(q)
    results = AssessmentResult.objects.filter(assignment__employee__branch=user.branch) if user.is_hr_admin else AssessmentResult.objects.all()
    if user.is_hr_admin and user.branch:
        results = results.filter(assignment__employee__branch=user.branch)
    return Response({
        'total_employees': employees.count(),
        'assessed_count': employees.filter(status='assessed').count(),
        'pending_count': employees.filter(status='pending').count(),
        'total_tasks': AssessmentTask.objects.filter(q).count(),
        'low_risk': results.filter(risk_level='low').count(),
        'medium_risk': results.filter(risk_level='medium').count(),
        'high_risk': results.filter(risk_level='high').count(),
    })

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = Employee.objects.all()
        user = self.request.user
        if user.is_hr_admin and user.branch:
            qs = qs.filter(branch=user.branch)
        s = self.request.query_params.get('search')
        if s:
            qs = qs.filter(Q(name__icontains=s) | Q(phone__icontains=s))
        return qs.order_by('-created_at')

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('category').all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = AssessmentTask.objects.select_related('template', 'branch', 'created_by').all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = AssessmentTask.objects.all()
        user = self.request.user
        if user.is_hr_admin and user.branch:
            qs = qs.filter(branch=user.branch)
        return qs.order_by('-created_at')

class ResultViewSet(viewsets.ModelViewSet):
    queryset = AssessmentResult.objects.select_related('session', 'assignment__employee', 'assignment__task').all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]
