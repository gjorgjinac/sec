from django.db import models


# Create your models here.

class Litigation(models.Model):
    release_no = models.CharField(max_length=15, unique=True)
    date = models.DateField(null=True, blank=True)
    respondents = models.CharField(max_length=1024)
    content = models.TextField(blank=True, null=True)
    people = models.CharField(max_length=1024, null=True)
    organizations = models.CharField(max_length=1024, null=True)
    objects = models.Manager()

    def __str__(self):
        return "release_no: {release_no}\ndate:{date}\nrespondents:{respondents}\ncontent:{content}\npeople:{people}\norgs:{organizations}".format(release_no=self.release_no,
                                                              date=self.date,
                                                              respondents=self.respondents,
                                                              content=self.content,
                                                              people=self.people,
                                                              organizations=self.organizations

                                                              )


class Reference(models.Model):
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True, related_name='litigation_fk_reference')
    reference = models.CharField(max_length=2000)
    reference_text = models.CharField(max_length=2000)
    objects = models.Manager()
    def __str__(self):
        return "reference text: {reference_text}\nreference link: {reference}".format(reference_text=self.reference_text, reference=self.reference)

def is_positive(value):
    return 0 < value < 7


class Title(models.Model):
    objects = models.Manager()
    litigation = models.ForeignKey(Litigation, on_delete=models.SET_NULL, blank=True, null=True, related_name='litigation_fk_title')
    title_text = models.CharField(max_length=1024, null=True, blank=True)
    priority = models.IntegerField(default=6, validators=[is_positive])  # h1 h2 h3
    def __str__(self):
        return "title: {title_text}\npriority: {priority}\n".format(title_text=self.title_text, priority=self.priority)
