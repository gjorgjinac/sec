from django.db import models


# Create your models here.

class Litigation(models.Model):
    release_no = models.CharField(max_length=15, unique=True)
    date = models.DateField(null=True, blank=True)
    respondents = models.CharField(max_length=1024)
    content = models.TextField(blank=True, null=True)
    people = models.CharField(max_length=1024, null=True)
    organizations = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return "{release_no} - {date} - {respondents}".format(release_no=self.release_no,
                                                              date=self.date,
                                                              respondents=self.respondents)


class Reference(models.Model):
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True)
    reference = models.CharField(max_length=2000)
    reference_text = models.CharField(max_length=2000)


def is_positive(value):
    return 0 < value < 7


class Title(models.Model):
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True)
    title_text = models.CharField(max_length=1024, null=True, blank=True)
    priority = models.IntegerField(default=6, validators=[is_positive])  # h1 h2 h3
