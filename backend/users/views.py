from api.paginators import CustomPagination
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser, Follow
from users.serializers import SubscribeSerializer, SubscriptionSerializer

STATUS_CREATED = status.HTTP_201_CREATED
STATUS_EMPTY = status.HTTP_204_NO_CONTENT


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = get_object_or_404(
            CustomUser, id=request.user.id,
        )
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = SubscriptionSerializer(
                pages,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=['post', 'delete'], detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        if request.method == 'POST':
            data = {'user': user.id, 'author': id}
            serializer = SubscribeSerializer(
                data=data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=STATUS_CREATED)
        following = get_object_or_404(CustomUser, id=id,)
        follow = get_object_or_404(Follow, user=user, author=following,)
        follow.delete()
        return Response(status=STATUS_EMPTY)
