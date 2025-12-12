from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProjectViewSet, ServiceCategoryViewSet,
    ServiceViewSet, TeamMemberViewSet, CEOViewSet, GalleryViewSet,
    ContactFormViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'service-categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'team-members', TeamMemberViewSet, basename='team-member')
router.register(r'ceo', CEOViewSet, basename='ceo')
router.register(r'gallery', GalleryViewSet, basename='gallery')
router.register(r'contact-forms', ContactFormViewSet, basename='contact-form')

urlpatterns = [
    path('', include(router.urls)),
]
