from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import AuthorAndTagFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeCreateSerializer,
                          CartSerializer, FavoriteSerializer)
from foodgram.models import Recipe, Tag, Ingredient, Amount, Cart, Favorite


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeListSerializer
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = AuthorAndTagFilter
    permission_classes = (IsAuthorOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method == 'POST' or 'PATCH':
            return RecipeCreateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request, pk=None):
        shopping_cart_obj = request.user.cart.all()
        cart_dict = {}
        for obj in shopping_cart_obj:
            recipes = obj.recipe
            ingredients = obj.recipe.ingredients.all()
            for ingredient in ingredients:
                amounts = Amount.objects.filter(
                    recipe=recipes, ingredient=ingredient
                )
                for amount in amounts:
                    if ingredient not in cart_dict:
                        cart_dict[ingredient] = amount.amount
                    else:
                        cart_dict[ingredient] = (amount.amount +
                                                 cart_dict[ingredient])
        with open('data/cart.txt', 'w', encoding='utf-8') as f:
            count = 0
            for ingredient, amount in cart_dict.items():
                count += 1
                f.writelines(
                    f'{count}. {str(ingredient.name).capitalize()} '
                    f'({ingredient.measurement_unit}) - {amount}\n'
                )
        return Response(
            {'status': 'Список покупок успешно выгружен'},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        request.data['user'] = self.request.user.id
        request.data['recipe'] = self.kwargs.get('pk')
        recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = CartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            cart = get_object_or_404(
                Cart, user=self.request.user, recipe=recipe
            )
            cart.delete()
            return Response(
                ({'message': f'Ингредиенты рецепта "{cart.recipe}" '
                             f'успешно удален из списка покупок'}),
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        request.data['user'] = self.request.user.id
        request.data['recipe'] = self.kwargs.get('pk')
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            favorite = get_object_or_404(
                Favorite, user=self.request.user, recipe=recipe
            )
            favorite.delete()
            return Response(
                ({'message': f'Рецепт "{favorite.recipe}" '
                             f'успешно удален из избранного'}),
                status=status.HTTP_204_NO_CONTENT
            )


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
