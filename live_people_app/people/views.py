from django.shortcuts import render

from .models import Person


def home(request):
    context = {'people': Person.objects.all()}
    return render(request, 'people/home.html', context=context)
