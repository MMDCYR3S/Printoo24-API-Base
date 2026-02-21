from rest_framework import serializers
from apps.home.models import SliderIndex

# ===== Slider Dashboard Serializer ===== #
class SliderDashboardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderIndex
        # فیلد link به لیست اضافه شد
        fields = ['id', 'name', 'image', 'image_url', 'link', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']
        extra_kwargs = {
            'image': {'write_only': True}
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None