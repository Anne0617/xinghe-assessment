import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from decimal import Decimal

from assessment.models import (
    TaskAssignment, AssessmentSession, Answer, AssessmentResult,
    AssessmentReport, Question, QuestionOption, TemplateQuestion,
)
from accounts.models import OperationLog


class EmployeeAccessView(TemplateView):
    """员工测评入口 - 输入测评码"""
    template_name = 'assessment/access.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['error'] = self.request.GET.get('error', '')
        return ctx

    def post(self, request):
        code = request.POST.get('code', '').strip()
        if not code:
            return redirect('/assessment/?error=请输入测评码')

        assign = TaskAssignment.objects.filter(access_code=code).select_related(
            'task__template', 'employee', 'task'
        ).first()

        if not assign:
            return redirect('/assessment/?error=测评码无效，请确认后重试')

        if assign.status == 'completed':
            return redirect('/assessment/?error=该测评已完成')

        if assign.status == 'expired':
            return redirect('/assessment/?error=该测评已超时过期')

        if assign.task.status != 'in_progress':
            return redirect('/assessment/?error=该测评任务已结束，请联系HR')

        # 检查有效期
        now = timezone.now()
        if now < assign.task.valid_from:
            return redirect('/assessment/?error=测评尚未开始，请在有效期内作答')
        if now > assign.task.valid_until:
            assign.status = 'expired'
            assign.save()
            return redirect('/assessment/?error=测评已过期')

        # 保存候选人填写的信息
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        if name:
            assign.employee.name = name
        if phone:
            assign.employee.phone = phone
        if email:
            assign.employee.email = email
        if any([name, phone, email]):
            assign.employee.save()

        return redirect('employee_take', code=code)


class EmployeeTakeView(TemplateView):
    """作答页面"""
    template_name = 'assessment/take.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.kwargs['code']
        assign = get_object_or_404(
            TaskAssignment.objects.select_related('task__template', 'employee'),
            access_code=code
        )

        # 检查是否已有进行中的会话
        session = AssessmentSession.objects.filter(
            assignment=assign, end_time__isnull=True
        ).first()

        if not session:
            # 创建新会话
            session = AssessmentSession.objects.create(assignment=assign)
            assign.status = 'in_progress'
            assign.save()

        # 获取模板题目
        template = assign.task.template
        tqs = TemplateQuestion.objects.filter(template=template) \
            .select_related('question__category') \
            .order_by('sort_order')

        questions = []
        for tq in tqs:
            q = tq.question
            opts = QuestionOption.objects.filter(question=q).order_by('sort_order')
            questions.append({
                'id': q.id,
                'text': q.text,
                'type': q.question_type,
                'is_reversed': q.is_reversed,
                'category': q.category.name,
                'options': [{'id': o.id, 'label': o.label, 'text': o.text, 'score': o.score} for o in opts],
            })

        ctx['assignment'] = assign
        ctx['questions'] = questions
        ctx['task'] = assign.task
        ctx['employee'] = assign.employee
        ctx['session'] = session
        ctx['duration_minutes'] = assign.task.duration_minutes
        ctx['questions_json'] = json.dumps(questions, ensure_ascii=False)
        return ctx


class EmployeeSubmitView(View):
    """提交作答"""
    def post(self, request, code):
        assign = get_object_or_404(TaskAssignment, access_code=code)
        session = AssessmentSession.objects.filter(assignment=assign, end_time__isnull=True).first()

        if not session:
            messages.error(request, '会话异常，请重新开始')
            return redirect('employee_access')

        with transaction.atomic():
            # 保存答案
            answers_data = {}
            total_score = Decimal('0')
            max_score = Decimal('0')
            dimension_scores = {}

            for key, value in request.POST.items():
                if key.startswith('q_'):
                    q_id = int(key[2:])
                    question = get_object_or_404(Question, pk=q_id)

                    # 计算得分
                    score = Decimal('0')
                    if question.question_type in ('likert5', 'likert7'):
                        score = Decimal(value)
                        if question.is_reversed:
                            # 反向计分: 6 - score (for 5级: 1->5, 2->4, etc.)
                            max_val = 5 if question.question_type == 'likert5' else 7
                            score = Decimal(max_val + 1) - score
                    else:
                        # 单选题/多选题
                        opt = QuestionOption.objects.filter(pk=int(value)).first()
                        if opt:
                            score = opt.score

                    # 保存答案
                    Answer.objects.create(
                        session=session,
                        question=question,
                        value=str(value),
                        score=score,
                    )

                    # 累加维度得分
                    cat_code = question.category.code
                    if cat_code not in dimension_scores:
                        dimension_scores[cat_code] = {
                            'name': question.category.name,
                            'score': Decimal('0'),
                            'max': Decimal('0'),
                            'count': 0,
                        }
                    dimension_scores[cat_code]['score'] += score
                    dimension_scores[cat_code]['max'] += question.score
                    dimension_scores[cat_code]['count'] += 1

                    total_score += score
                    max_score += question.score

            # 计算得分率
            score_percent = (total_score / max_score * 100) if max_score > 0 else Decimal('0')

            # 计算各维度得分和风险等级
            dimension_result = {}
            risk_tags = []
            risk_count = 0
            for code, ds in dimension_scores.items():
                percent = (ds['score'] / ds['max'] * 100) if ds['max'] > 0 else Decimal('0')
                if percent < 40:
                    level = '高风险'
                    risk_tags.append(f'{ds["name"]}偏低')
                    risk_count += 1
                elif percent < 60:
                    level = '中风险'
                    risk_tags.append(f'{ds["name"]}需关注')
                else:
                    level = '良好'
                dimension_result[code] = {
                    'name': ds['name'],
                    'score': float(ds['score']),
                    'max': float(ds['max']),
                    'percent': float(percent),
                    'level': level,
                }

            # 计算适配度
            fit_score = float(score_percent)
            if fit_score >= 70:
                risk_level = 'low'
            elif fit_score >= 50:
                risk_level = 'medium'
            else:
                risk_level = 'high'

            # 异常检测
            duration = int((timezone.now() - session.start_time).total_seconds())
            is_abnormal = duration < 60  # 1分钟内提交判为异常

            # 更新会话
            session.end_time = timezone.now()
            session.duration_seconds = duration
            session.is_valid = not is_abnormal
            if is_abnormal:
                session.invalid_reason = '作答时间过短'
            session.save()

            # 创建结果
            result = AssessmentResult.objects.create(
                session=session,
                assignment=assign,
                total_score=float(total_score),
                max_score=float(max_score),
                score_percent=float(score_percent),
                dimension_scores=dimension_result,
                risk_tags=risk_tags,
                risk_level=risk_level,
                fit_score=fit_score,
                is_abnormal=is_abnormal,
                abnormal_reason=session.invalid_reason,
            )

            # 生成简易报告
            generate_report(result)

            # 更新分配状态
            assign.status = 'completed'
            assign.completed_at = timezone.now()
            assign.save()

            # 更新员工状态
            assign.employee.status = 'assessed'
            assign.employee.save()

            OperationLog.objects.create(
                action=f'员工 {assign.employee.name} 完成测评 {assign.task.name}'
            )

        return redirect('employee_thanks')


def generate_report(result):
    """生成测评报告"""
    dims = result.dimension_scores
    employee = result.assignment.employee
    task = result.assignment.task

    html_parts = []
    html_parts.append(f'<h2>{employee.name} - 入职人才测评报告</h2>')
    html_parts.append(f'<p>岗位: {employee.position} | 测评任务: {task.name}</p>')
    html_parts.append(f'<p>测评时间: {result.generated_at.strftime("%Y-%m-%d %H:%M")}</p>')
    html_parts.append(f'<p><strong>综合得分率: {result.score_percent:.1f}%</strong></p>')
    html_parts.append(f'<p><strong>岗位适配度: {result.fit_score:.1f}</strong></p>')
    html_parts.append(f'<p>风险等级: {"低风险" if result.risk_level=="low" else "中风险" if result.risk_level=="medium" else "高风险"}</p>')

    if result.risk_tags:
        html_parts.append('<p>关注项: ' + ', '.join(result.risk_tags) + '</p>')

    html_parts.append('<h3>各维度得分</h3><table border="1" cellpadding="6" style="border-collapse:collapse;width:100%;">')
    html_parts.append('<tr><th>维度</th><th>得分</th><th>满分</th><th>得分率</th><th>评估</th></tr>')
    for code, d in dims.items():
        html_parts.append(f'<tr><td>{d["name"]}</td><td>{d["score"]:.1f}</td><td>{d["max"]:.1f}</td><td>{d["percent"]:.1f}%</td><td>{d["level"]}</td></tr>')
    html_parts.append('</table>')

    if result.is_abnormal:
        html_parts.append(f'<p style="color:red;">注意: 该测评可能存在异常 ({result.abnormal_reason})，建议HR复核</p>')

    AssessmentReport.objects.create(
        result=result,
        html_content=''.join(html_parts),
    )


class EmployeeResultView(TemplateView):
    """测评结果页"""
    template_name = 'assessment/result.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        code = self.kwargs['code']
        assign = get_object_or_404(
            TaskAssignment.objects.select_related('employee', 'task__template'),
            access_code=code
        )
        result = AssessmentResult.objects.filter(assignment=assign).first()
        report = AssessmentReport.objects.filter(result=result).first() if result else None

        ctx['assignment'] = assign
        ctx['result'] = result
        ctx['report'] = report
        ctx['employee'] = assign.employee
        return ctx


class EmployeeThanksView(TemplateView):
    """提交后的感谢页面"""
    template_name = 'assessment/thanks.html'
