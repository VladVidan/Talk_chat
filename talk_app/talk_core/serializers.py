from django.contrib.auth.password_validation import validate_password
from requests import Response
from rest_framework import serializers, status
from talk_core.models import CustomUser
from rest_framework.response import Response


class EmailLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'password']


class UsernameRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']


class PhotoProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField()

    class Meta:
        model = CustomUser
        fields = ['profile_photo']


class ChangePasswordAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['old_password', 'password']

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Incorrect password.'})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username"]

    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This user already in use."})
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data["username"]
        instance.save()
        return instance
