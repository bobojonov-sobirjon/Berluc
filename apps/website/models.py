from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

class Category(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True)
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'Category #{self.pk}' if self.pk else 'New Category'
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = '01. Категории'
        

class Project(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
        short_description = models.TextField(_("Краткое описание"), null=True, blank=True),
        brand = models.CharField(_("Бренд"), max_length=255, null=True, blank=True),
        country = models.CharField(_("Страна"), max_length=255, null=True, blank=True),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True, blank=True)
    material = models.CharField(_("Материал"), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'Project #{self.pk}' if self.pk else 'New Project'
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = '02. Проекты'
        

class ProjectItem(TranslatableModel):
    translations = TranslatedFields(
        color = models.JSONField(_("Цвета"), null=True, blank=True, default=list, help_text='Список цветов в формате JSON, например: ["красный", "синий", "зеленый"]'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_items', verbose_name='Проект', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Старая цена', null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Скидка', null=True, blank=True)
    width = models.IntegerField(verbose_name='Ширина', null=True, blank=True)
    height = models.IntegerField(verbose_name='Высота', null=True, blank=True)
    depth = models.IntegerField(verbose_name='Глубина', null=True, blank=True)
    weight = models.IntegerField(verbose_name='Вес', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        if self.project:
            try:
                project_name = str(self.project)
            except Exception:
                project_name = f'Project #{self.project.pk}'
            colors = []
            current_lang = self.get_current_language()
            for lang_code in ['ru', 'uz']:
                try:
                    if self.has_translation(lang_code):
                        self.set_current_language(lang_code)
                        color = self.color
                        if color:
                            if isinstance(color, list):
                                colors.extend([str(c) for c in color])
                            else:
                                colors.append(str(color))
                except Exception:
                    pass
            if current_lang:
                self.set_current_language(current_lang)
            if colors:
                return f'Item: {project_name} - {", ".join(set(colors))}'
            return f'Item: {project_name}'
        return f'ProjectItem #{self.pk}' if self.pk else 'New ProjectItem'
    
    class Meta:
        verbose_name = 'Элемент проекта'
        verbose_name_plural = '03. Элементы проекта'


class ProjectImage(models.Model):
    project_item = models.ForeignKey(ProjectItem, on_delete=models.CASCADE, related_name='images', verbose_name='Элемент проекта', null=True, blank=True)
    image = models.ImageField(upload_to='projects/', verbose_name='Изображение', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    objects = models.Manager()
    
    def __str__(self):
        if self.project_item:
            try:
                project_name = str(self.project_item.project) if self.project_item.project else f'Item #{self.project_item.pk}'
            except Exception:
                project_name = f'Item #{self.project_item.pk}'
            return f'Image: {project_name}'
        return f'Image #{self.pk}' if self.pk else 'New Image'
    
    class Meta:
        verbose_name = 'Изображение проекта'
        verbose_name_plural = 'Изображения проекта'


class ProjectVideo(models.Model):
    project_item = models.ForeignKey(ProjectItem, on_delete=models.CASCADE, related_name='videos', verbose_name='Элемент проекта', null=True, blank=True)
    video = models.FileField(upload_to='projects/', verbose_name='Видео', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    objects = models.Manager()
    
    def __str__(self):
        if self.project_item:
            try:
                project_name = str(self.project_item.project) if self.project_item.project else f'Item #{self.project_item.pk}'
            except Exception:
                project_name = f'Item #{self.project_item.pk}'
            return f'Video: {project_name}'
        return f'Video #{self.pk}' if self.pk else 'New Video'
    
    class Meta:
        verbose_name = 'Видео проекта'
        verbose_name_plural = 'Видео проекта'
        

class ProjectSEO(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Заголовок"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
        keywords = models.TextField(_("Ключевые слова"), null=True, blank=True),
    )
    project_item = models.ForeignKey(ProjectItem, on_delete=models.CASCADE, related_name='seo', verbose_name='Элемент проекта', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        if self.project_item:
            try:
                project_name = str(self.project_item.project) if self.project_item.project else f'Item #{self.project_item.pk}'
            except Exception:
                project_name = f'Item #{self.project_item.pk}'
            titles = []
            current_lang = self.get_current_language()
            for lang_code in ['ru', 'uz']:
                try:
                    if self.has_translation(lang_code):
                        self.set_current_language(lang_code)
                        title = self.title
                        if title and str(title).strip():
                            titles.append(f"{title} ({lang_code})")
                except Exception:
                    pass
            if current_lang:
                self.set_current_language(current_lang)
            if titles:
                return f'SEO: {project_name} - {" / ".join(titles)}'
            return f'SEO: {project_name}'
        return f'SEO #{self.pk}' if self.pk else 'New SEO'
    
    class Meta:
        verbose_name = 'SEO проекта'
        verbose_name_plural = 'SEO проекта'
        

class ServiceCategory(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True)
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'ServiceCategory #{self.pk}' if self.pk else 'New ServiceCategory'
    
    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = '04. Категории услуг'


class Service(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
    )
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name='Категория', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'Service #{self.pk}' if self.pk else 'New Service'
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = '05. Услуги'


class ServiceItem(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True),
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_items', verbose_name='Услуга', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'ServiceItem #{self.pk}' if self.pk else 'New ServiceItem'
    
    class Meta:
        verbose_name = 'Элемент услуги'
        verbose_name_plural = '05. Элементы услуги'


class ServiceDetail(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True),
    )
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE, related_name='service_details', verbose_name='Элемент услуги', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'ServiceDetail #{self.pk}' if self.pk else 'New ServiceDetail'
    
    class Meta:
        verbose_name = 'Деталь услуги'
        verbose_name_plural = 'Детали услуг'


class TeamMember(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Имя"), max_length=255, null=True, blank=True),
        position = models.CharField(_("Должность"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
    )
    image = models.ImageField(upload_to='team/', verbose_name='Изображение', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'TeamMember #{self.pk}' if self.pk else 'New TeamMember'
    
    class Meta:
        verbose_name = 'Участник команды'
        verbose_name_plural = '07. Участники команды'
        
    
class CEO(TranslatableModel):
    class TypePage(models.TextChoices):
        ABOUT = 'about'
        TEAM = 'team'
        CONTACT = 'contact'
        SERVICE = 'service'
        PROJECT = 'project'
        MAIN = 'main'
        GALLERY = 'gallery'
        
    translations = TranslatedFields(
        name = models.CharField(_("Имя"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
    )
    type = models.CharField(max_length=255, verbose_name='Тип', null=True, blank=True, choices=TypePage.choices)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'CEO #{self.pk}' if self.pk else 'New CEO'
    
    class Meta:
        verbose_name = 'CEO'
        verbose_name_plural = '07. CEO'


class Gallery(TranslatableModel):
    translations = TranslatedFields(
        name = models.CharField(_("Название"), max_length=255, null=True, blank=True),
        description = models.TextField(_("Описание"), null=True, blank=True),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        names = []
        current_lang = self.get_current_language()
        for lang_code in ['ru', 'uz']:
            try:
                if self.has_translation(lang_code):
                    self.set_current_language(lang_code)
                    name = self.name
                    if name and str(name).strip():
                        names.append(f"{name} ({lang_code})")
            except Exception:
                pass
        if current_lang:
            self.set_current_language(current_lang)
        if names:
            return ' / '.join(names)
        return f'Gallery #{self.pk}' if self.pk else 'New Gallery'
    
    class Meta:
        verbose_name = 'Галерея'
        verbose_name_plural = '09. Галереи'


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images', verbose_name='Галерея', null=True, blank=True)
    image = models.ImageField(upload_to='gallery/', verbose_name='Изображение', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    objects = models.Manager()
    
    def __str__(self):
        if self.gallery:
            try:
                gallery_name = str(self.gallery)
            except Exception:
                gallery_name = f'Gallery #{self.gallery.pk}'
            return f'Image: {gallery_name}'
        return f'Image #{self.pk}' if self.pk else 'New Image'
    
    class Meta:
        verbose_name = 'Изображение галереи'
        verbose_name_plural = 'Изображения галереи'


class ContactForm(models.Model):
    name = models.CharField(_("Имя"), max_length=255, null=True, blank=True)
    phone = models.CharField(_("Телефон"), max_length=20, null=True, blank=True)
    email = models.EmailField(_("Email"), null=True, blank=True)
    message = models.TextField(_("Сообщение"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    
    def __str__(self):
        return f'{self.name or "No name"} - {self.email or "No email"}' if self.pk else 'New ContactForm'
    
    class Meta:
        verbose_name = 'Форма обратной связи'
        verbose_name_plural = '10. Формы обратной связи'
        
