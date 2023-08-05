from rest_framework import serializers
from django.contrib.auth.models import User

class EmailLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']