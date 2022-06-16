from django.contrib import admin
from .models import (Recipe, Amount, Cart, Tag,
                     Favorite, Follow, Ingredient)


class AmountInline(admin.TabularInline):
    model = Amount


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        AmountInline
    ]
    list_display = ['name', 'author']
    list_filter = ('author', 'name', 'tags',)
    fields = [
        ('author', 'name', 'image'),
        'get_add_to_favorite_count',
        'text', ('tags', 'cooking_time')
    ]
    readonly_fields = ('get_add_to_favorite_count',)

    def get_add_to_favorite_count(self, instance):
        return (instance.favorites.count())

    get_add_to_favorite_count.short_description = (
        'Количество добавлений в избранное'
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'following']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
