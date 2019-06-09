import os
from django.db import models


# Create your models here.

class Litigation(models.Model):
    release_no = models.CharField(max_length=15, unique=True)
    date = models.DateField(null=True, blank=True)
    respondents = models.CharField(max_length=1024)
    content = models.TextField(blank=True, null=True)
    people = models.CharField(max_length=1024, null=True)
    organizations = models.CharField(max_length=1024, null=True)
    date_modified = models.DateField(null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        fields = (f'release_no={self.release_no}',
                  f'date={self.date}',
                  f'date_modified:{self.date_modified}',
                  f'respondents={self.respondents}',
                  f'people={self.people}',
                  f'organizations={self.organizations}',
                  f'content={self.content}')
        return f'[{os.linesep.join(fields)}]'


class Reference(models.Model):
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='litigation_fk_reference')
    reference = models.CharField(max_length=2000)
    reference_text = models.CharField(max_length=2000)
    release_no = models.CharField(max_length=15, unique=False)
    objects = models.Manager()

    def __str__(self):
        return f'reference text={self.reference_text}{os.linesep}reference link={self.reference}{os.linesep}release_no={self.release_no}'


def is_positive(value):
    return 0 < value < 7


class Title(models.Model):
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='litigation_fk_title')
    title_text = models.CharField(max_length=1024, null=True, blank=True)
    priority = models.IntegerField(default=6, validators=[is_positive])  # h1 h2 h3
    release_no = models.CharField(max_length=15, unique=False)
    objects = models.Manager()

    def __str__(self):
        return f"title={self.title_text}{os.linesep}priority={self.priority}{os.linesep}release_no={self.release_no}"
