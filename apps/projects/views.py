from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Project, UploadedFile, Question, Task
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    UploadedFileSerializer,
    QuestionSerializer,
    CreateTaskSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        import os, shutil, logging
        _log = logging.getLogger(__name__)
        deleted_count = 0

        for f in instance.files.all():
            try:
                if f.file and os.path.isfile(f.file.path):
                    os.remove(f.file.path)
                    deleted_count += 1
            except Exception as e:
                _log.warning(f"Failed to delete uploaded file: {e}")

        for q in instance.questions.all():
            try:
                if q.result_image and os.path.isfile(q.result_image.path):
                    os.remove(q.result_image.path)
                    deleted_count += 1
            except Exception as e:
                _log.warning(f"Failed to delete result image: {e}")

        _log.info(f"Project {instance.id} deleted, cleaned up {deleted_count} files")
        instance.delete()

    @action(detail=True, methods=['post'])
    def upload_file(self, request, pk=None):
        project = self.get_object()
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': '请选择文件'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.files.parsers import parse_file
        file_name = uploaded_file.name
        file_type = file_name.split('.')[-1].lower()
        file_size = uploaded_file.size

        instance = UploadedFile.objects.create(
            project=project,
            file=uploaded_file,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
        )

        try:
            parsed = parse_file(instance.file.path, file_type)
            instance.parsed_content = parsed
            instance.save()
        except Exception:
            pass

        return Response(UploadedFileSerializer(instance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def start_task(self, request, pk=None):
        project = self.get_object()
        serializer = CreateTaskSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        task = Task.objects.create(project=project, status='pending')
        project.status = 'processing'
        project.save()

        provider = serializer.validated_data['provider']
        enable_web_search = serializer.validated_data.get('enable_web_search', False)

        # 后台线程执行流水线，避免阻塞 HTTP 响应
        import threading
        def _run():
            _run_pipeline_direct(str(task.id), provider, enable_web_search)
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        return Response({
            'task_id': str(task.id),
            'status': task.status,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        project = self.get_object()
        content = request.data.get('content', '')
        order = request.data.get('order', project.questions.count() + 1)

        question = Question.objects.create(
            project=project,
            order=order,
            content=content,
            analysis='',
            formula='',
            code='',
            result_text='',
            result_image='',
        )
        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        project = self.get_object()
        return Response(QuestionSerializer(project.questions.all(), many=True).data)

    @action(detail=True, methods=['post'])
    def extract_questions(self, request, pk=None):
        project = self.get_object()

        from apps.accounts.models import UserAPIKey
        from apps.agent.llm.base import create_llm_client
        provider = request.data.get('provider', 'deepseek')
        api_key_obj = UserAPIKey.objects.filter(user=request.user, provider=provider, is_active=True).first()
        if not api_key_obj:
            return Response({'error': '未绑定该模型的 API Key'}, status=status.HTTP_400_BAD_REQUEST)

        client = create_llm_client(api_key_obj)

        # 搜集附件内容
        file_contents = []
        for f in project.files.all():
            if f.parsed_content:
                file_contents.append(f"--- {f.file_name} ---\n{f.parsed_content[:3000]}")
        extra_context = "\n\n".join(file_contents) if file_contents else ""

        prompt = f"""分析以下数学建模题目，提取出每一小问的内容。返回 JSON 数组格式：
[{{"order": 1, "content": "第1问内容"}}, ...]

题目描述：
{project.description}

附件内容：
{extra_context}

注意：如果题目在附件中，请仔细从附件中提取每一问的完整文本。只返回 JSON 数组。"""
        raw = client.chat_sync(prompt)
        import json, re, logging
        _logger = logging.getLogger(__name__)

        questions_data = None
        candidates = []

        # 策略1: 去掉 markdown 代码块标记再匹配 JSON 数组
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', raw)
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if match:
            candidates.append(match.group())

        # 策略2: 匹配 JSON 对象
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            candidates.append(match.group())

        # 策略3: 原始文本
        candidates.append(raw.strip())

        parse_error = None
        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    questions_data = parsed
                elif isinstance(parsed, dict):
                    questions_data = [parsed]
                break
            except (json.JSONDecodeError, ValueError) as e:
                parse_error = str(e)
                continue

        if questions_data is None:
            _logger.warning(f"Failed to parse AI response, fallback to whole problem as question: {raw[:500]}")
            fallback_content = project.description.strip() or extra_context[:3000].strip()
            if not fallback_content:
                return Response({
                    'error': '未能从题目或附件中提取到有效内容，请补充题目描述后重试。'
                }, status=status.HTTP_400_BAD_REQUEST)
            questions_data = [{
                'order': 1,
                'content': fallback_content,
            }]

        question_instances = []
        project.questions.all().delete()
        for q_data in questions_data:
            q = Question.objects.create(
                project=project,
                order=q_data['order'],
                content=q_data['content'],
                analysis='',
                formula='',
                code='',
                result_text='',
                result_image='',
            )
            question_instances.append(q)

        return Response(QuestionSerializer(question_instances, many=True).data)


class UploadedFileViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UploadedFile.objects.filter(project__user=self.request.user)


class TaskViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        qs = Task.objects.filter(project__user=self.request.user)
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    @action(detail=True, methods=['get'])
    def thinking(self, request, pk=None):
        task = self.get_object()
        return Response({'thinking_log': task.thinking_log})


def _run_pipeline_direct(task_id: str, provider: str, enable_web_search: bool = False):
    """直接执行流水线（后台线程），替代 Celery"""
    import logging
    _log = logging.getLogger(__name__)

    from django.db import connections
    connections.close_all()

    from apps.projects.models import Task
    from apps.accounts.models import UserAPIKey
    from apps.agent.cli_agent import CLIAgent
    from apps.agent.llm.base import create_llm_client
    from apps.projects.consumers import push_agent_thought

    try:
        task = Task.objects.get(id=task_id)
        project = task.project
    except Task.DoesNotExist:
        _log.error(f"Task {task_id} not found")
        return

    api_key_obj = UserAPIKey.objects.filter(
        user=project.user, provider=provider, is_active=True
    ).first()
    if not api_key_obj:
        task.status = 'failed'
        task.error_message = f"未找到 {provider} 的有效 API Key"
        task.save()
        push_agent_thought(str(task_id), {
            "type": "thinking",
            "content": f"❌ 未找到 {provider} 的有效 API Key",
            "status": "failed",
        })
        return

    llm_client = create_llm_client(api_key_obj)

    def push_callback(data):
        task.refresh_from_db()
        thinking_log = task.thinking_log or []
        thinking_log.append(data)
        task.thinking_log = thinking_log
        task.save()
        push_agent_thought(str(task_id), data)

    def update_status(status):
        task.refresh_from_db()
        task.status = status
        task.save()

    agent = CLIAgent(llm_client=llm_client, push_callback=push_callback)
    try:
        agent.run_pipeline(
            project=project,
            task=task,
            update_status_callback=update_status,
            enable_web_search=enable_web_search,
        )
        task.refresh_from_db()
        task.status = 'done'
        task.save()
    except Exception as e:
        try:
            task.refresh_from_db()
        except Exception:
            pass
        task.status = 'failed'
        task.error_message = str(e)[:500]
        task.save()
        _log.exception(f"Agent pipeline failed: {e}")
