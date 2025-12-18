from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, NumberFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import (
    Category, Project, ProjectImage, ProjectVideo, ProjectSEO,
    ServiceCategory, Service, ServiceItem, ServiceDetail,
    TeamMember, CEO, Gallery, ContactForm
)
from .serializers import (
    CategorySerializer, ProjectSerializer, ServiceCategorySerializer,
    ServiceSerializer, TeamMemberSerializer, CEOSerializer, GallerySerializer,
    ContactFormSerializer
)


@extend_schema(
    tags=['Categories'],
    summary='Get all categories',
    description='Returns a list of all categories with translations (ru/uz)'
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Category model.
    Returns categories with translations in Russian and Uzbek.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProjectFilter(FilterSet):
    name = CharFilter(method='filter_by_name')
    category = NumberFilter(field_name='category_id')
    brand = CharFilter(method='filter_by_brand')
    material = CharFilter(field_name='material', lookup_expr='icontains')
    color = CharFilter(method='filter_by_color')
    
    def filter_by_name(self, queryset, name, value):
        return queryset.filter(translations__name__icontains=value).distinct()
    
    def filter_by_brand(self, queryset, name, value):
        return queryset.filter(translations__brand__icontains=value).distinct()
    
    def filter_by_color(self, queryset, name, value):
        from django.db import connection
        
        # JSONField ichida qidirish
        # SQLite da JSONField uchun icontains ishlamaydi, shuning uchun Python da filter qilamiz
        # Color list bo'lishi mumkin, shuning uchun har bir translation da tekshirish
        
        # To'g'ridan-to'g'ri SQL query ishlatish, recursion dan qochish uchun
        with connection.cursor() as cursor:
            # ProjectTranslation jadvalidan color fieldni olish
            cursor.execute("""
                SELECT DISTINCT master_id, color 
                FROM website_project_translation 
                WHERE color IS NOT NULL
            """)
            
            project_ids = set()
            for row in cursor.fetchall():
                master_id = row[0]
                color_json = row[1]
                
                if master_id and color_json:
                    try:
                        import json
                        color = json.loads(color_json) if isinstance(color_json, str) else color_json
                        
                        if color:
                            if isinstance(color, list):
                                # List ichida qidirish
                                if any(str(c).lower().find(value.lower()) != -1 for c in color if c):
                                    project_ids.add(master_id)
                            elif isinstance(color, str):
                                # String ichida qidirish
                                if value.lower() in color.lower():
                                    project_ids.add(master_id)
                    except Exception:
                        pass
        
        if project_ids:
            return queryset.filter(id__in=project_ids).distinct()
        
        # Agar hech qanday translation topilmasa, bo'sh queryset qaytarish
        return queryset.none()
    
    class Meta:
        model = Project
        fields = ['name', 'category', 'brand', 'material', 'color']


@extend_schema(
    tags=['Projects'],
    summary='Get all projects',
    description='Returns a list of projects with translations, images, videos, and SEO data. Supports pagination and filtering.',
    parameters=[
        OpenApiParameter('limit', OpenApiTypes.INT, description='Limit the number of results (disables pagination)'),
        OpenApiParameter('name', OpenApiTypes.STR, description='Filter by project name'),
        OpenApiParameter('category', OpenApiTypes.INT, description='Filter by category ID'),
        OpenApiParameter('brand', OpenApiTypes.STR, description='Filter by brand name'),
        OpenApiParameter('material', OpenApiTypes.STR, description='Filter by material'),
        OpenApiParameter('color', OpenApiTypes.STR, description='Filter by color'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in name and brand fields'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by field (e.g., -created_at, price)'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
    ]
)
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Project model.
    Returns projects with translations (ru/uz), colors, prices, dimensions, images, videos, and SEO data.
    Supports pagination, filtering by name, category, brand, material, color, and limit.
    """
    queryset = Project.objects.prefetch_related(
        'images',
        'videos',
        'seo'
    ).select_related('category')
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['translations__name', 'translations__brand']
    ordering_fields = ['created_at', 'price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit', None)
        if limit:
            try:
                limit = int(limit)
                if limit > 0:
                    queryset = queryset[:limit]
            except ValueError:
                pass
        return queryset
    
    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', None)
        if limit:
            self.pagination_class = None
        return super().list(request, *args, **kwargs)


@extend_schema(
    tags=['Service Categories'],
    summary='Get all service categories',
    description='Returns a list of all service categories with translations (ru/uz)'
)
class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ServiceCategory model.
    Returns service categories with translations in Russian and Uzbek.
    """
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


class ServiceFilter(FilterSet):
    category = NumberFilter(field_name='category_id')
    
    class Meta:
        model = Service
        fields = ['category']


@extend_schema(
    tags=['Services'],
    summary='Get all services',
    description='Returns a list of services with translations, service items, and service details. Supports filtering by category.',
    parameters=[
        OpenApiParameter('category', OpenApiTypes.INT, description='Filter by service category ID'),
    ]
)
class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Service model.
    Returns services with translations (ru/uz), service items, and service details.
    Supports filtering by service category.
    """
    queryset = Service.objects.prefetch_related(
        'service_items__service_details'
    ).select_related('category')
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter


@extend_schema(
    tags=['Team Members'],
    summary='Get all team members',
    description='Returns a list of all team members with translations (ru/uz) and images'
)
class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for TeamMember model.
    Returns team members with translations in Russian and Uzbek, and images.
    """
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@extend_schema(
    tags=['CEO'],
    summary='Get CEO information',
    description='Returns CEO information with translations (ru/uz)'
)
class CEOViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for CEO model.
    Returns CEO information with translations in Russian and Uzbek.
    """
    queryset = CEO.objects.all()
    serializer_class = CEOSerializer


@extend_schema(
    tags=['Gallery'],
    summary='Get all gallery images',
    description='Returns a list of all gallery images with full URLs'
)
class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Gallery model.
    Returns gallery images with full URLs.
    """
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@extend_schema(
    tags=['Contact Forms'],
    summary='Create contact form',
    description='Submit a contact form with name, phone, email, and message. Returns the created contact form.',
    request=ContactFormSerializer,
    responses={201: ContactFormSerializer}
)
class ContactFormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ContactForm model.
    Supports only POST to create new contact forms.
    """
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    http_method_names = ['post']



#hello world    