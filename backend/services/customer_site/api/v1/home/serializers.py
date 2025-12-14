from rest_framework import serializers
from core.models import SliderIndex, PromotionalModal, ContactUs

# ===== Slider Serializer ===== #
class SliderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderIndex
        fields = ['id', 'name', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    
# ===== Promotional Modal Serializer ===== #
class PromotionalModalSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PromotionalModal
        fields = ['id', 'title', 'description', 'image_url', 'cta_text', 'cta_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

# ===== Contact Us Serializer ===== #
class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'phone_number', 'subject', 'message']