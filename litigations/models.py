import os
from django.db import models


'''A model contains the essential fields and behaviors of the data you’re storing. Generally, each model maps to a single database table.
Each model is a Python class that subclasses django.db.models.Model.
Each attribute of the model represents a database field.

Each field takes a certain set of field-specific arguments (all of them are optional):
    null - If True, Django will store empty values as NULL in the database. Default is False.
    blank - If True, the field is allowed to be blank. Default is False.
    primary_key - If True, this field is the primary key for the model. If you don’t specify primary_key=True for any fields in your model, 
    Django will automatically add an IntegerField to hold the primary key
    unique - If True, this field must be unique throughout the table.
    default - The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created.
    further reading: https://docs.djangoproject.com/en/2.2/topics/db/models/
    
Model managers are inherited from abstract base classes and enable query execution. 
    '''
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
        fields = (f'release_no={self.release_no}',
                  f'reference text={self.reference_text}',
                  f'reference link={self.reference}')
        return f'[{os.linesep.join(fields)}]'


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
        fields = (f'release_no={self.release_no}',
                  f'title={self.title_text}',
                  f'priority={self.priority}')
        return f'[{os.linesep.join(fields)}]'
