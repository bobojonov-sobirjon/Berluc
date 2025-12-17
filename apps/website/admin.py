from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from parler.admin import TranslatableAdmin, TranslatableStackedInline, TranslatableTabularInline
from .models import (
    Category, Project, ProjectItem, ProjectImage, ProjectVideo, ProjectSEO,
    ServiceCategory, Service, ServiceItem, ServiceDetail,
    TeamMember, CEO, Gallery, GalleryImage, ContactForm
)
from .forms import ProjectAdminForm


def get_translation_status(obj):
    """Umumiy metod: qaysi tillarda to'ldirilganligini ko'rsatadi"""
    if not obj or not obj.pk:
        return format_html('<span style="color: #999;">-</span>')
    
    statuses = []
    for lang_code, lang_name in [('ru', 'RU'), ('uz', 'UZ')]:
        try:
            has_trans = obj.has_translation(lang_code)
            if has_trans:
                current_lang = obj.get_current_language()
                obj.set_current_language(lang_code)
                try:
                    main_field = None
                    if hasattr(obj, 'name'):
                        main_field = obj.name
                    elif hasattr(obj, 'title'):
                        main_field = obj.title
                    elif hasattr(obj, 'color'):
                        main_field = obj.color
                        if isinstance(main_field, list):
                            main_field = ', '.join([str(c) for c in main_field if c]) if main_field else None
                        elif main_field:
                            main_field = str(main_field)
                    
                    if main_field and str(main_field).strip():
                        statuses.append(format_html('<span style="color: green; font-weight: bold;">{}: ✓</span>', lang_name))
                    else:
                        statuses.append(format_html('<span style="color: red;">{}: ✗</span>', lang_name))
                finally:
                    if current_lang:
                        obj.set_current_language(current_lang)
            else:
                statuses.append(format_html('<span style="color: red;">{}: ✗</span>', lang_name))
        except Exception as e:
            statuses.append(format_html('<span style="color: red;">{}: ✗</span>', lang_name))
    
    if statuses:
        return mark_safe(' | '.join([str(s) for s in statuses]))
    return format_html('<span style="color: #999;">-</span>')


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ['get_name', 'get_translation_status', 'created_at']
    list_filter = ['created_at']
    search_fields = ['translations__name']
    date_hierarchy = 'created_at'
    
    def get_name(self, obj):
        if obj and obj.pk:
            try:
                return obj.name or '-'
            except Exception:
                return str(obj) if obj else '-'
        return '-'
    get_name.short_description = 'Название'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        kwargs = kwargs or {}
        form_class = super().get_form(request, obj, **kwargs)
        # Customize form fields if it's a form class
        if hasattr(form_class, 'base_fields'):
            for field_name, field in form_class.base_fields.items():
                if 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({'style': 'width: 70%;'})
        return form_class
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'get_image_preview', 'created_at')
    readonly_fields = ('get_image_preview', 'created_at')
    fk_name = 'project_item'
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return '-'
    get_image_preview.short_description = 'Превью'


class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1
    fields = ('video', 'created_at')
    readonly_fields = ('created_at',)
    fk_name = 'project_item'


class ProjectSEOInline(TranslatableStackedInline):
    model = ProjectSEO
    extra = 1
    fields = ('title', 'description', 'keywords', 'created_at')
    readonly_fields = ('created_at',)
    inline_tabs = True
    fk_name = 'project_item'


@admin.register(Project)
class ProjectAdmin(TranslatableAdmin):
    form = ProjectAdminForm
    list_display = ['name', 'get_translation_status']
    list_filter = ['category', 'created_at']
    search_fields = ['translations__name', 'translations__brand', 'translations__country']
    date_hierarchy = 'created_at'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'description' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4 if 'description' in field_name.lower() and 'short' not in field_name.lower() else 3,
                        'cols': 80,
                        'style': 'width: 70%; height: {}px;'.format('100' if 'description' in field_name.lower() and 'short' not in field_name.lower() else '80')
                    })
            elif any(x in field_name.lower() for x in ['name', 'brand', 'country', 'material']):
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({
                        'style': 'width: 70%;'
                    })
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description', 'short_description')
        }),
        ('Дополнительная информация', {
            'fields': ('brand', 'country', 'material')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ProjectItem)
class ProjectItemAdmin(TranslatableAdmin):
    list_display = ['get_item_name', 'get_translation_status', 'project', 'price', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['project__translations__name', 'translations__color']
    date_hierarchy = 'created_at'
    inlines = [ProjectImageInline, ProjectVideoInline, ProjectSEOInline]
    
    def get_item_name(self, obj):
        if obj.project:
            try:
                project_name = str(obj.project)
            except Exception:
                project_name = f'Project #{obj.project.pk}'
            colors = []
            current_lang = obj.get_current_language()
            for lang_code in ['ru', 'uz']:
                try:
                    if obj.has_translation(lang_code):
                        obj.set_current_language(lang_code)
                        color = obj.color
                        if color:
                            if isinstance(color, list):
                                colors.extend([str(c) for c in color])
                            else:
                                colors.append(str(color))
                except Exception:
                    pass
            if current_lang:
                obj.set_current_language(current_lang)
            if colors:
                return f'{project_name} - {", ".join(set(colors))}'
            return project_name
        return f'Item #{obj.pk}' if obj.pk else 'New Item'
    get_item_name.short_description = 'Элемент проекта'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        from .forms import ColorInputWidget
        kwargs = kwargs or {}
        form = super().get_form(request, obj, **kwargs)
        if hasattr(form, 'base_fields'):
            for field_name, field in form.base_fields.items():
                if 'color' in field_name.lower():
                    # Ensure field is JSONField and widget is properly set
                    field.widget = ColorInputWidget()
                    # Make sure field accepts JSON string
                    if hasattr(field, 'to_python'):
                        # Field is already JSONField, no need to change
                        pass
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'color', 'created_at')
        }),
        ('Цена и скидки', {
            'fields': ('price', 'old_price', 'discount')
        }),
        ('Размеры', {
            'fields': ('width', 'height', 'depth', 'weight')
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'created_at']
    list_filter = ['created_at']
    search_fields = ['translations__name']
    date_hierarchy = 'created_at'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',)
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


class ServiceDetailInline(TranslatableTabularInline):
    model = ServiceDetail
    extra = 1
    fields = ('name', 'created_at')
    readonly_fields = ('created_at',)
    inline_tabs = True
    fk_name = 'service_item'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form


@admin.register(Service)
class ServiceAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['translations__name', 'translations__description']
    date_hierarchy = 'created_at'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'description' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4,
                        'cols': 80,
                        'style': 'width: 70%; height: 100px;'
                    })
            elif 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'category', 'description')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ServiceItem)
class ServiceItemAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'service', 'created_at']
    list_filter = ['service', 'created_at']
    search_fields = ['translations__name', 'service__translations__name']
    date_hierarchy = 'created_at'
    inlines = [ServiceDetailInline]
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'service', 'created_at')
        }),
    )
    
    readonly_fields = ['created_at']
    
#     def get_translation_status(self, obj):
#         return get_translation_status(obj)
#     get_translation_status.short_description = 'Переводы'
    
#     class Media:
#         css = {
#             'all': ('admin/css/custom_admin.css',)
#         }
#         js = ('admin/js/custom_admin.js',)
    
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         for field_name, field in form.base_fields.items():
#             if 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
#                 field.widget.attrs.update({'style': 'width: 70%;'})
#         return form
    
#     fieldsets = (
#         ('Основная информация', {
#             'fields': ('name', 'service')
#         }),
#         ('Дополнительно', {
#             'fields': ('created_at',),
#             'classes': ('collapse',)
#         }),
#     )
    
#     readonly_fields = ['created_at']


@admin.register(TeamMember)
class TeamMemberAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'position', 'get_image_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['translations__name', 'translations__position', 'translations__description']
    date_hierarchy = 'created_at'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return '-'
    get_image_preview.short_description = 'Фото'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'description' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4,
                        'cols': 80,
                        'style': 'width: 70%; height: 100px;'
                    })
            elif any(x in field_name.lower() for x in ['name', 'position']) and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'position', 'image', 'description')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(CEO)
class CEOAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'type', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['translations__name', 'translations__description']
    date_hierarchy = 'created_at'
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'description' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4,
                        'cols': 80,
                        'style': 'width: 70%; height: 100px;'
                    })
            elif 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'type', 'description')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ('image', 'get_image_preview', 'created_at')
    readonly_fields = ('get_image_preview', 'created_at')
    fk_name = 'gallery'
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return '-'
    get_image_preview.short_description = 'Превью'


@admin.register(Gallery)
class GalleryAdmin(TranslatableAdmin):
    list_display = ['name', 'get_translation_status', 'created_at']
    list_filter = ['created_at']
    search_fields = ['translations__name', 'translations__description']
    date_hierarchy = 'created_at'
    inlines = [GalleryImageInline]
    
    def get_translation_status(self, obj):
        return get_translation_status(obj)
    get_translation_status.short_description = 'Переводы'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'description' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4,
                        'cols': 80,
                        'style': 'width: 70%; height: 100px;'
                    })
            elif 'name' in field_name.lower() and hasattr(field.widget, 'attrs'):
                field.widget.attrs.update({'style': 'width: 70%;'})
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'get_message_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'phone', 'email', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def get_message_preview(self, obj):
        if obj.message:
            return format_html('<span title="{}">{}</span>', obj.message, obj.message[:50] + '...' if len(obj.message) > 50 else obj.message)
        return '-'
    get_message_preview.short_description = 'Сообщение'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if 'message' in field_name.lower():
                if isinstance(field.widget, forms.Textarea) or hasattr(field.widget, 'attrs'):
                    field.widget = forms.Textarea(attrs={
                        'rows': 4,
                        'cols': 80,
                        'style': 'width: 70%; height: 100px;'
                    })
            elif 'name' in field_name.lower() or 'phone' in field_name.lower() or 'email' in field_name.lower():
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({
                        'style': 'width: 70%;'
                    })
        return form
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone', 'email', 'message')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
