# coding=utf-8
from factory import DjangoModelFactory, Faker

from .models import Person


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    dob = Faker('date')
    zip = Faker('postalcode')
