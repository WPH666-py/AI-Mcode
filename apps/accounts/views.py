from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import UserAPIKey
from .serializers import UserAPIKeySerializer


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'detail': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({'detail': '注册成功', 'username': user.username}, status=status.HTTP_201_CREATED)


class UserAPIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = UserAPIKeySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserAPIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
