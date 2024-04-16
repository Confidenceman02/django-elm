from django.db import models


class Car(models.Model):
    manufacturer = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.manufacturer


class Driver(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Enthusiast(models.Model):
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=100, blank=True)


class Team(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
