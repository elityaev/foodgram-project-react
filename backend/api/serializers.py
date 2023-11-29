from drf_extra_fields.fields import Base64ImageField

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from foodgram.models import (Recipe, Tag, Ingredient,
                             Amount, Favorite, Cart, Follow)
from users.models import User
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        validators = [
            UniqueTogetherValidator(
                queryset=Amount.objects.all(),
                fields=('ingredient', 'recipe',)
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeListSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        return AmountSerializer(
            Amount.objects.filter(recipe=obj), many=True
        ).data

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated and (
                Favorite.objects.filter(
                    user=self.context['request'].user, recipe=obj
                                        ).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated and (
                Cart.objects.filter(
                    user=self.context['request'].user, recipe=obj).exists()):
            return True
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = SerializerMethodField()
    tags = SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

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

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        Amount.objects.filter(recipe=instance).all().delete()
        ingredient_amount_data = self.initial_data.get('ingredients')
        for ingredient_amount in ingredient_amount_data:
            ingredient_id = ingredient_amount.get('id')
            amount = ingredient_amount.get('amount')
            Amount.objects.create(
                recipe=instance,
                ingredient_id=ingredient_id,
                amount=amount
            )
        instance.save()
        return instance

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
        fields = ('id', 'name', 'image', 'cooking_time',)

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
        fields = ('id', 'name', 'image', 'cooking_time',)

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
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
