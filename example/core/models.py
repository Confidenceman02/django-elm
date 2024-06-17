from django.db import models


# Create your models here.
class Extra(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Promotion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    extras = models.ManyToManyField(Extra)
