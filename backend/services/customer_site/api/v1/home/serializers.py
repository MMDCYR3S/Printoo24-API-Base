from rest_framework import serializers
from core.models import SliderIndex

# ===== Slider Serializer ===== #
class SliderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderIndex
        fields = ['id', 'name', 'image_url', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None