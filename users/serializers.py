from rest_framework import serializers
from .models import Users


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Users model.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        exclude = ["groups", "user_permissions"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # Here we call the custom manager's create_user or create_admin_user method
        # based on the value of the is_staff field
        if validated_data.get("is_staff"):
            return Users.objects.create_admin_user(**validated_data)
        return Users.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Remove the password field from the validated data if it is provided
        validated_data.pop("password", None)

        # Remove the email field from the validated data if it is provided
        validated_data.pop("email", None)

        # Update the user instance with the validated data
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # save the user instance
        instance.save()

        return instance
