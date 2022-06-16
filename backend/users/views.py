from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import FollowSerializer
from foodgram.models import Follow
from .models import User
from .serializers import (UserSerializer, SetPasswordSerializer,
                          GetTokenSerializer, CreateUserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        me = User.objects.get(id=request.user.id)
        serializer = UserSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        if request.data['current_password'] == request.user.password:
            serializer = SetPasswordSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(password=request.data['new_password'])
            return Response(
                {'message': 'Пароль успешно изменен'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'error': 'Введен неверный текущий пароль'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        followers = self.request.user.follower.all()
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            following = get_object_or_404(User, pk=pk)

            request.data.update(
                dict(user=f'{request.user.id}', following=f'{following.id}')
            )
            serializer = FollowSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(following=following, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            following = get_object_or_404(User, pk=pk)
            try:
                follow = Follow.objects.get(
                    user=request.user, following=following
                )
            except Exception as error:
                return Response(
                    {'error': f'Ошибка отписки: "{error}"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow.delete()
        return Response(
            {'message': f'Вы отписались от пользователя {following}'},
            status=status.HTTP_204_NO_CONTENT
        )


class GetToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return Response(
                {'email': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)
        token = Token.objects.get_or_create(user=user)
        return Response({'auth_token': str(token[0])})


class DeleteToken(APIView):

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(
            {'message': 'Вы вышли из аккаунта'},
            status=status.HTTP_204_NO_CONTENT
        )
