from uuid import uuid4

from django.db import models
from model_utils.models import TimeStampedModel


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField('first name', max_length=30)
    last_name = models.CharField('last name', max_length=30)
    dob = models.CharField('date of birth', max_length=30)
    zip = models.CharField('zip code', max_length=10)

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['-created', 'last_name', 'first_name']

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __repr__(self):
        PersonClass = self.__class__

        return "<%s: %s>" % (PersonClass.__name__, self.name)

    def __str__(self):
        return self.name
