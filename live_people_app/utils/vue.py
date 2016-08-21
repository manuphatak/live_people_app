# coding=utf-8
from django import forms

from . import css


class ModelForm(forms.ModelForm):
    input_classes = 'form-control'
    group_classes = 'form-group'
    vue_model = NotImplemented

    def as_vue(self):
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <small class="form-text text-muted">%s</small>',
            errors_on_separate_row=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in self._meta.fields:
            field = self.fields[name]
            attrs = field.widget.attrs
            bound_field = self[name]

            # update widget attrs
            attrs.update({
                'class': css.join(self.input_classes, attrs.get('class')),
                'v-model': '.'.join((self.vue_model, name)),
                'placeholder': field.label.lower(),
            })

            bound_field.css_classes = css.include(bound_field.css_classes, self.group_classes)
