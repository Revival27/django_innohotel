from rest_framework import serializers

class DeviceSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    address = serializers.CharField(max_length=255)