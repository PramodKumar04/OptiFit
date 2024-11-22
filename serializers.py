# user_profile/serializers.py
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'age', 'gender', 'height', 'weight', 'fitness_goal', 'bmi']
