from django.contrib.auth.password_validation import validate_password
from requests import Response
from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.response import Response


class EmailLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']


class UsernameRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ChangePasswordAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["old_password", 'password', 'password_confirm']

    def validate(self, attr):
        if attr['password'] != attr["password_confirm"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attr

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()

        return instance


class UpdateLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True , write_only=True)


    class Meta:
        model = User
        fields = ["username"]

    def validate_username(self,value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This user already in use."})
        return value

    def update(self,instance , validated_data):
        instance.username = validated_data["username"]
        instance.save()
        return instance
