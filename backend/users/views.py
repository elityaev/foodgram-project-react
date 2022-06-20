from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPagination
from api.serializers import FollowSerializer
from foodgram.models import Follow
from .models import User


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            following = get_object_or_404(User, pk=id)

            request.data.update(
                dict(user=f'{request.user.id}', following=f'{following.id}')
            )
            serializer = FollowSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=following, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            following = get_object_or_404(User, pk=id)
            try:
                follow = Follow.objects.get(
                    user=request.user, author=following
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
