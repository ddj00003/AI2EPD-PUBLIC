from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    collection_name = serializers.CharField()
        
