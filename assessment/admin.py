from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    QuestionCategory, Question, QuestionOption,
    AssessmentTemplate, TemplateQuestion,
    Employee, AssessmentTask, TaskAssignment,
    AssessmentSession, Answer, AssessmentResult,
    AssessmentReport, NotificationTemplate, SystemConfig
)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 3


class TemplateQuestionInline(admin.TabularInline):
    model = TemplateQuestion
    extra = 5


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ['question', 'value', 'score', 'created_at']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'code']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'question_type', 'category', 'score', 'weight', 'is_reversed', 'is_active', 'review_status']
    list_filter = ['question_type', 'category', 'is_active', 'review_status', 'is_reversed']
    search_fields = ['text', 'category__name']
    list_editable = ['is_active', 'review_status']
    inlines = [QuestionOptionInline]
    fieldsets = (
        ('基本信息', {'fields': ('question_type', 'category', 'text', 'description')}),
        ('计分设置', {'fields': ('score', 'weight', 'is_reversed')}),
        ('状态', {'fields': ('is_active', 'review_status', 'created_by')}),
    )
    readonly_fields = ['created_at', 'updated_at']

    def text_preview(self, obj):
        return obj.text[:60]
    text_preview.short_description = '题目内容'


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_position', 'estimated_minutes', 'total_questions', 'is_active']
    list_filter = ['is_active', 'target_position']
    search_fields = ['name', 'description']
    inlines = [TemplateQuestionInline]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'position', 'branch', 'status', 'phone', 'created_at']
    list_filter = ['status', 'branch', 'gender', 'position']
    search_fields = ['name', 'phone', 'position', 'department']
    list_editable = ['status']


@admin.register(AssessmentTask)
class AssessmentTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'branch', 'status', 'valid_from', 'valid_until', 'created_by']
    list_filter = ['status', 'branch', 'template']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ['task', 'employee', 'status', 'access_code', 'assigned_at', 'completed_at']
    list_filter = ['status', 'task__branch']
    search_fields = ['employee__name', 'access_code', 'task__name']
    readonly_fields = ['assigned_at']


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'assignment', 'start_time', 'end_time', 'duration_seconds', 'is_valid']
    list_filter = ['is_valid', 'is_timeout']
    inlines = [AnswerInline]


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'total_score', 'score_percent', 'risk_level', 'fit_score', 'is_abnormal']
    list_filter = ['risk_level', 'is_abnormal']
    search_fields = ['assignment__employee__name']
    readonly_fields = ['generated_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'is_active']
    list_filter = ['channel', 'is_active']


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description']
    search_fields = ['key', 'description']
