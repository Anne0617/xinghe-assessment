from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class Branch(models.Model):
    """分公司"""
    name = models.CharField('分公司名称', max_length=100)
    code = models.CharField('分公司代码', max_length=20, unique=True, help_text='如 GZ、YD、SZ 等')
    address = models.CharField('地址', max_length=200, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    is_active = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '分公司'
        verbose_name_plural = '分公司'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """自定义用户模型"""
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', '超级管理员'
        HR_ADMIN = 'hr_admin', 'HR管理员'

    role = models.CharField('角色', max_length=20, choices=Role.choices, default=Role.HR_ADMIN)
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL,
        verbose_name='所属分公司', null=True, blank=True,
        help_text='超管可不关联分公司'
    )
    phone = models.CharField('手机号', max_length=20, blank=True)
    department = models.CharField('所属部门', max_length=100, blank=True)
    is_locked = models.BooleanField('是否冻结', default=False)

    # 权限细分
    can_manage_questions = models.BooleanField('题库管理权限', default=False)
    can_manage_tasks = models.BooleanField('测评任务权限', default=False)
    can_view_data = models.BooleanField('数据查看权限', default=False)
    can_export_data = models.BooleanField('数据导出权限', default=False)
    can_manage_employees = models.BooleanField('员工管理权限', default=False)

    class Meta:
        verbose_name = '管理员账号'
        verbose_name_plural = '管理员账号'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_hr_admin(self):
        return self.role == self.Role.HR_ADMIN

    def save(self, *args, **kwargs):
        if self.is_super_admin:
            self.can_manage_questions = True
            self.can_manage_tasks = True
            self.can_view_data = True
            self.can_export_data = True
            self.can_manage_employees = True
        super().save(*args, **kwargs)


class OperationLog(models.Model):
    """操作日志"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    action = models.CharField('操作', max_length=50, help_text='如 登录、创建任务、导出报告')
    detail = models.TextField('详情', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.action} ({self.created_at:%Y-%m-%d %H:%M})'
