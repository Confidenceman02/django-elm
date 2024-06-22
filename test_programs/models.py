from django.db import models


class Car(models.Model):
    manufacturer = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.manufacturer


class Extra(models.Model):
    name = models.CharField(max_length=100)


class Extra01(models.Model):
    name = models.CharField(max_length=100)


class Driver(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Blank(models.Model):
    first = models.CharField(max_length=100, null=True)
    second = models.CharField(max_length=100, null=True)
    third = models.BooleanField()
    fourth = models.IntegerField()
    fifth = models.FloatField()


class BlankM(models.Model):
    first = models.CharField(max_length=100, null=True)
    second = models.CharField(max_length=100, null=True)
    third = models.BooleanField()
    fourth = models.IntegerField()
    fifth = models.FloatField()


class Blanks(models.Model):
    blank = models.ForeignKey(Blank, on_delete=models.SET_NULL, null=True)
    blanks = models.ManyToManyField(BlankM)


class Enthusiast(models.Model):
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=100, blank=True)
    extras = models.ManyToManyField(Extra)
    extras01 = models.ManyToManyField(Extra01)


class Team(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
