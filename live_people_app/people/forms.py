# coding=utf-8
from django import forms
from django.utils.html import strip_tags

from .models import Person
from ..utils import vue


class DateInput(forms.DateInput):
    input_type = 'date'


class PersonForm(vue.ModelForm):
    vue_model = 'person'

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'dob', 'zip']
        widgets = {
            'dob': DateInput(),
        }

    def clean_dob(self):
        return strip_tags(self.cleaned_data['dob'])

    def clean_first_name(self):
        return strip_tags(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return strip_tags(self.cleaned_data['last_name'])

    def clean_zip(self):
        return strip_tags(self.cleaned_data['zip'])


class NewPersonForm(PersonForm):
    input_classes = 'form-control form-control-sm'
    vue_model = 'newPerson'

    class Meta(PersonForm.Meta):
        pass


class UpdatePersonForm(PersonForm):
    vue_model = 'person.fields'

    class Meta(PersonForm.Meta):
        pass
