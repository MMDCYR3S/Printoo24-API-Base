from rest_framework import serializers

# ===== Cart Item File Upload Serializer ===== #
class CartItemFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
