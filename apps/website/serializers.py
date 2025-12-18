from rest_framework import serializers
from .models import (
    Category, Project, ProjectImage, ProjectVideo, ProjectSEO,
    ServiceCategory, Service, ServiceItem, ServiceDetail,
    TeamMember, CEO, Gallery, GalleryImage, ContactForm
)


class TranslationSerializer(serializers.Serializer):
    ru = serializers.DictField(required=False)
    uz = serializers.DictField(required=False)


class CategorySerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = Category
        fields = ['id', 'translations', 'created_at']


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'created_at']


class ProjectVideoSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    
    def get_video(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None
    
    class Meta:
        model = ProjectVideo
        fields = ['id', 'video', 'created_at']


class ProjectSEOSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'title': obj.title,
                        'description': obj.description,
                        'keywords': obj.keywords
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = ProjectSEO
        fields = ['id', 'translations', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name,
                        'description': obj.description,
                        'short_description': obj.short_description,
                        'brand': obj.brand,
                        'country': obj.country
                    }
            except Exception:
                pass
        return result
    
    def get_images(self, obj):
        images = obj.images.all()
        return ProjectImageSerializer(images, many=True, context=self.context).data
    
    def get_videos(self, obj):
        videos = obj.videos.all()
        return ProjectVideoSerializer(videos, many=True, context=self.context).data
    
    def get_seo(self, obj):
        seo = obj.seo.all()
        return ProjectSEOSerializer(seo, many=True, context=self.context).data
    
    class Meta:
        model = Project
        fields = [
            'id', 'translations', 'category', 'material',
            'images', 'videos', 'seo', 'created_at'
        ]


class ServiceCategorySerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        current_lang = obj.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    name = getattr(obj, 'name', None)
                    if name and str(name).strip():
                        result[lang_code] = {
                            'name': name
                        }
            except Exception:
                pass
            finally:
                # Original language ni qaytarish
                if current_lang:
                    try:
                        obj.set_current_language(current_lang)
                    except Exception:
                        pass
        return result
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'translations', 'created_at']


class ServiceDetailSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = ServiceDetail
        fields = ['id', 'translations', 'created_at']


class ServiceItemSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    service_details = ServiceDetailSerializer(many=True, read_only=True)
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = ServiceItem
        fields = ['id', 'translations', 'service_details', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    category = ServiceCategorySerializer(read_only=True)
    service_items = ServiceItemSerializer(many=True, read_only=True)
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name,
                        'description': obj.description
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = Service
        fields = ['id', 'translations', 'category', 'service_items', 'created_at']


class TeamMemberSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name,
                        'position': obj.position,
                        'description': obj.description
                    }
            except Exception:
                pass
        return result
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    class Meta:
        model = TeamMember
        fields = ['id', 'translations', 'image', 'created_at']


class CEOSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name,
                        'description': obj.description
                    }
            except Exception:
                pass
        return result
    
    class Meta:
        model = CEO
        fields = ['id', 'translations', 'type', 'created_at']


class GalleryImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'created_at']


class GallerySerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    def get_translations(self, obj):
        result = {}
        for lang_code in ['ru', 'uz']:
            try:
                if obj.has_translation(lang_code):
                    obj.set_current_language(lang_code)
                    result[lang_code] = {
                        'name': obj.name,
                        'description': obj.description
                    }
            except Exception:
                pass
        return result
    
    def get_images(self, obj):
        images = obj.images.all()
        return GalleryImageSerializer(images, many=True, context=self.context).data
    
    class Meta:
        model = Gallery
        fields = ['id', 'translations', 'images', 'created_at']


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = ['id', 'name', 'phone', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

