# serializers.py
from rest_framework import serializers
from .models import ManagerPersonalDetails

from django.contrib.auth.models import User

class ManagerPersonalDetailsSerializer(serializers.ModelSerializer):
    email = serializers.CharField()

    class Meta:
        model = ManagerPersonalDetails
        fields = '__all__'

    def create(self, validated_data):
        # Get email value from validated data
        email_username = validated_data.pop('email')
        
        # Retrieve the User instance based on the email username
        try:
            user = User.objects.get(username=email_username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        # Set the User instance as the email field in validated_data
        validated_data['email'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Extract the email string from validated data
        email_username = validated_data.get('email', None)

        # If email is provided, update it with the corresponding User instance
        if email_username:
            try:
                user = User.objects.get(username=email_username)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "User with this email does not exist."})
            validated_data['email'] = user

        # Call the parent class's update method to handle the actual update
        return super().update(instance, validated_data)
