from django_filters import rest_framework as filters

from foodgram.models import Recipe, User


# class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
#     pass
#
# class RecipeFilter(filters.FilterSet):
#     tags = CharFilterInFilter(field_name='tags__slug', lookup_expr='in')
#     author = filters.CharFilter()
#     is_favorited = filters.CharFilter(method='is_favorited')
#     # is_in_shopping_cart =
#
#     class Meta:
#         model = Recipe
#         fields = ['tags', 'author']
#
#     def is_favorited(self, queryset, name, value):
#         print(value)
#         if value == 1:
#             return queryset.filter(is_favorited=True)
#         if value == 0:
#             return queryset.filter(is_favorited=False)


class AuthorAndTagFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        print(value)
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        print(value)
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
