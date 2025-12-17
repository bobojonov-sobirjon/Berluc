from django import forms
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from .models import Project
import json
from parler.forms import TranslatableModelForm


class ColorInputWidget(forms.Widget):
    """Custom widget for color field with add/remove functionality"""
    
    template_name = 'admin/website/projectitem/color_widget.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        # Parse value to get colors list
        colors = []
        if value:
            try:
                if isinstance(value, str):
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(value)
                        if isinstance(parsed, list):
                            colors = parsed
                    except (json.JSONDecodeError, ValueError):
                        # If not JSON, treat as single value
                        if value.strip():
                            colors = [value.strip()]
                elif isinstance(value, list):
                    colors = value
            except (TypeError, AttributeError):
                pass
        
        # Generate HTML for color inputs
        container_id = f'color-inputs-container-{name}'
        html = f'<div id="{container_id}" style="margin-bottom: 10px;">'
        
        if colors:
            for idx, color in enumerate(colors):
                color_value = escape(str(color)) if color else ''
                html += f'''
                <div class="color-input-row" style="display: flex; margin-bottom: 5px; align-items: center;">
                    <input type="text" class="color-input" value="{color_value}" placeholder="Название цвета" 
                           style="flex: 1; padding: 5px; margin-right: 5px; border: 1px solid #ddd; border-radius: 3px;">
                    <button type="button" class="remove-color-btn" style="padding: 5px 10px; background: #dc3545; color: white; border: none; cursor: pointer; border-radius: 3px;">Удалить</button>
                </div>
                '''
        else:
            html += '''
            <div class="color-input-row" style="display: flex; margin-bottom: 5px; align-items: center;">
                <input type="text" class="color-input" value="" placeholder="Название цвета" 
                       style="flex: 1; padding: 5px; margin-right: 5px;">
                <button type="button" class="remove-color-btn" style="padding: 5px 10px; background: #dc3545; color: white; border: none; cursor: pointer;">Удалить</button>
            </div>
            '''
        
        html += '</div>'
        html += f'''
        <button type="button" id="add-color-btn-{name}" style="padding: 8px 15px; background: #28a745; color: white; border: none; cursor: pointer; margin-bottom: 10px; border-radius: 3px; font-weight: bold;">+ Добавить цвет</button>
        <input type="hidden" name="{name}" id="color-json-input-{name}" value='{escape(json.dumps(colors, ensure_ascii=False))}'>
        '''
        
        html += f'''
        <script>
        (function() {{
            const fieldName = '{name}';
            const containerId = 'color-inputs-container-{name}';
            const addBtnId = 'add-color-btn-{name}';
            const hiddenInputId = 'color-json-input-{name}';
            
            function updateColorJSON() {{
                const container = document.getElementById(containerId);
                const inputs = container.querySelectorAll('.color-input');
                const colors = [];
                inputs.forEach(function(input) {{
                    const value = input.value.trim();
                    if (value) {{
                        colors.push(value);
                    }}
                }});
                document.getElementById(hiddenInputId).value = JSON.stringify(colors);
            }}
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', init);
            }} else {{
                init();
            }}
            
            function init() {{
                const addBtn = document.getElementById(addBtnId);
                if (!addBtn) return;
                
                // Add color button
                addBtn.addEventListener('click', function() {{
                    const container = document.getElementById(containerId);
                    const newRow = document.createElement('div');
                    newRow.className = 'color-input-row';
                    newRow.style.cssText = 'display: flex; margin-bottom: 5px; align-items: center;';
                    newRow.innerHTML = `
                        <input type="text" class="color-input" value="" placeholder="Название цвета" 
                               style="flex: 1; padding: 5px; margin-right: 5px; border: 1px solid #ddd; border-radius: 3px;">
                        <button type="button" class="remove-color-btn" style="padding: 5px 10px; background: #dc3545; color: white; border: none; cursor: pointer; border-radius: 3px;">Удалить</button>
                    `;
                    container.appendChild(newRow);
                    
                    // Add remove event
                    newRow.querySelector('.remove-color-btn').addEventListener('click', function() {{
                        newRow.remove();
                        updateColorJSON();
                    }});
                    
                    // Add input event
                    newRow.querySelector('.color-input').addEventListener('input', updateColorJSON);
                }});
                
                // Remove color buttons
                const container = document.getElementById(containerId);
                if (container) {{
                    container.querySelectorAll('.remove-color-btn').forEach(function(btn) {{
                        btn.addEventListener('click', function() {{
                            this.closest('.color-input-row').remove();
                            updateColorJSON();
                        }});
                    }});
                    
                    // Input events
                    container.querySelectorAll('.color-input').forEach(function(input) {{
                        input.addEventListener('input', updateColorJSON);
                    }});
                }}
            }}
        }})();
        </script>
        '''
        
        return mark_safe(html)
    
    def value_from_datadict(self, data, files, name):
        """Return JSON string, not list - Django JSONField expects string"""
        json_value = data.get(name, '[]')
        try:
            if isinstance(json_value, list):
                # Convert list to JSON string
                return json.dumps(json_value, ensure_ascii=False)
            if isinstance(json_value, str):
                # Validate it's valid JSON, then return as string
                parsed = json.loads(json_value)
                return json.dumps(parsed, ensure_ascii=False)
            return '[]'
        except (json.JSONDecodeError, ValueError, TypeError):
            return '[]'


class ProjectAdminForm(TranslatableModelForm):
    """Custom form for Project with better color field handling"""
    
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name.startswith('color_'):
                field.widget = ColorInputWidget()
                field.required = False
                field.help_text = 'Нажмите "+ Добавить цвет" для добавления нового цвета'
                
                if self.instance and self.instance.pk:
                    try:
                        lang_code = field_name.split('_', 1)[1] if '_' in field_name else None
                        if lang_code:
                            current_lang = self.instance.get_current_language()
                            self.instance.set_current_language(lang_code)
                            try:
                                color_value = self.instance.color
                                if color_value:
                                    if isinstance(color_value, list):
                                        self.initial[field_name] = color_value
                                    else:
                                        self.initial[field_name] = []
                                else:
                                    self.initial[field_name] = []
                            except Exception:
                                self.initial[field_name] = []
                            finally:
                                if current_lang:
                                    self.instance.set_current_language(current_lang)
                    except Exception:
                        pass

    def clean(self):
        cleaned_data = super().clean()
        
        for field_name in list(cleaned_data.keys()):
            if field_name.startswith('color_'):
                color_data = cleaned_data.get(field_name, '[]')
                if not color_data:
                    cleaned_data[field_name] = []
                else:
                    try:
                        if isinstance(color_data, list):
                            cleaned_data[field_name] = [str(c).strip() for c in color_data if c and str(c).strip()]
                        elif isinstance(color_data, str):
                            parsed = json.loads(color_data)
                            if isinstance(parsed, list):
                                cleaned_data[field_name] = [str(c).strip() for c in parsed if c and str(c).strip()]
                            else:
                                cleaned_data[field_name] = []
                        else:
                            cleaned_data[field_name] = []
                    except (json.JSONDecodeError, ValueError, TypeError):
                        cleaned_data[field_name] = []
        
        return cleaned_data

