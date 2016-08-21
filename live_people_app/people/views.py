from django.shortcuts import render

from .forms import NewPersonForm


def home(request):
    context = {'new_person_form': NewPersonForm()}
    return render(request, 'people/home.html', context=context)
