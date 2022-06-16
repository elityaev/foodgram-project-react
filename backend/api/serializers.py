from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from foodgram.models import (Recipe, Tag, Ingredient,
                             Amount, Favorite, Cart, Follow)
from users.serializers import UserSerializer

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ['id', 'name', 'measurement_unit', 'amount']
        validators = [
            UniqueTogetherValidator(
                queryset=Amount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class RecipeListSerializer(serializers.ModelSerializer):
    image = serializers.URLField()
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_ingredients(self, obj):
        return AmountSerializer(
            Amount.objects.filter(recipe=obj), many=True
        ).data

    def get_is_favorited(self, obj):
        try:
            if Favorite.objects.filter(
                    user=self.context['request'].user, recipe=obj).exists():
                return True
            else:
                return False
        except TypeError:
            return False

    def get_is_in_shopping_cart(self, obj):
        try:
            if Cart.objects.filter(
                    user=self.context['request'].user, recipe=obj
            ).exists():
                return True
            else:
                return False
        except TypeError:
            return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = SerializerMethodField()
    tags = SerializerMethodField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        ]

    def create(self, validate_data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(**validate_data)
        for tag in tags:
            tag_object = Tag.objects.get(id=tag)
            recipe.tags.add(tag_object)
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            ing = Ingredient.objects.get(id=ingredient_id)
            amount = ingredient.get('amount')
            Amount.objects.create(
                recipe=recipe,
                ingredient=ing,
                amount=amount
            )
        return recipe

    def get_tags(self, obj):
        return TagSerializer(
            Tag.objects.filter(recipe=obj), many=True
        ).data

    def get_ingredients(self, obj):
        return AmountSerializer(
            Amount.objects.filter(recipe=obj), many=True
        ).data


class CartSerializer(serializers.ModelSerializer):
    id = SerializerMethodField()
    name = SerializerMethodField()
    image = SerializerMethodField()
    cooking_time = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_id(self, obj):
        return obj.recipe.id

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return str(obj.recipe.image)

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    def validate(self, data):
        user = get_object_or_404(User, pk=self.initial_data['user'])
        recipe = get_object_or_404(Recipe, pk=int(self.initial_data['recipe']))
        if Cart.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(
                'Ингредиенты этого рецепта уже в вашем списке покупок'
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    id = SerializerMethodField()
    name = SerializerMethodField()
    image = SerializerMethodField()
    cooking_time = SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_id(self, obj):
        return obj.recipe.id

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return str(obj.recipe.image)

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    def validate(self, data):
        user = get_object_or_404(User, pk=self.initial_data['user'])
        recipe = get_object_or_404(Recipe, pk=int(self.initial_data['recipe']))
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError('Рецепт уже в избранном')
        return data


class FollowRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = serializers.ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, source='following.email')
    id = serializers.IntegerField(source='following.id')
    username = serializers.CharField(
        max_length=150, source='following.username'
    )
    first_name = serializers.CharField(
        max_length=150, source='following.first_name'
    )
    last_name = serializers.CharField(
        max_length=150, source='following.last_name'
    )
    recipe = SerializerMethodField()
    recipe_count = SerializerMethodField()

    def validate(self, data):
        user = get_object_or_404(User, pk=self.initial_data['user'])
        following = get_object_or_404(User, pk=self.initial_data['following'])
        if self.initial_data['user'] == self.initial_data['following']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя!'
            )
        elif Follow.objects.filter(user=user, following=following).exists():
            raise ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return data

    class Meta:
        model = Follow
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'recipe', 'recipe_count']

    def get_recipe(self, obj):
        recipe_obj = obj.following.recipes.all()
        return FollowRecipeSerializer(recipe_obj, many=True).data

    def get_recipe_count(self, obj):
        return (obj.following.recipes.count())
