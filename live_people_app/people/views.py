from django.shortcuts import render

from .forms import NewPersonForm, UpdatePersonForm


def home(request):
    context = {
        'new_person_form': NewPersonForm(),
        'update_person_form': UpdatePersonForm(),
    }
    return render(request, 'people/home.html', context=context)
