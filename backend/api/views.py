from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                        ShoppingCart, Tag)
from api.paginators import CustomPagination
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             ShoppingCartSerializer, TagSerializer)


class RetrieveListViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=FavoriteRecipe)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount', 'recipe__name'
        )
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2],
                    'recipe': item[3]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('DejaVuSans', './data/DejaVuSans.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('DejaVuSans', size=24)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('DejaVuSans', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'{data["recipe"]}:'
                                         f'{i}. {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
