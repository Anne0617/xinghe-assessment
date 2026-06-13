from rest_framework import serializers
from accounts.models import User, Branch
from assessment.models import Employee, QuestionCategory, Question, AssessmentTemplate, AssessmentTask, AssessmentResult

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'role', 'branch', 'is_super_admin']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Question
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    class Meta:
        model = AssessmentTask
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='assignment.employee.name', read_only=True)
    task_name = serializers.CharField(source='assignment.task.name', read_only=True)
    class Meta:
        model = AssessmentResult
        fields = '__all__'

class DashboardStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    assessed_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    low_risk = serializers.IntegerField()
    medium_risk = serializers.IntegerField()
    high_risk = serializers.IntegerField()
