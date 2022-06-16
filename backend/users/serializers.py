from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from foodgram.models import Follow
from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        try:
            if Follow.objects.filter(
                    user=self.context['request'].user, following=obj).exists():
                return True
            else:
                return False
        except TypeError:
            return False


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name']


class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True, max_length=150)
    current_password = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = ['new_password', 'current_password']


class GetTokenSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, max_length=150
    )
    email = serializers.EmailField(
        write_only=True, required=True, max_length=254
    )
    auth_token = serializers.CharField(read_only=True, max_length=255)

    class Meta:
        model = User
        fields = ['password', 'email', 'auth_token']
