from django.db import models
from django.contrib.auth.models import User
from menu.models import models as menuModels


type_choices = (('CHEF', 'CHEF'), ('DELIVERY', 'DELIVERY'))


class Customer(models.Model):
    user = models.OneToOneField(User, related_name='customer')
    user_type = models.CharField(max_length=10, default='CUSTOMER')
    is_vip = models.BooleanField(default=False)
    balance = models.FloatField()
    numOrders = models.PositiveIntegerField(default=0)
    spending = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    address  = models.TextField(null=True)
    rep = models.PositiveIntegerField(default=3)
    deregistered = models.BooleanField(default=False)

    def approve (self):
        self.is_approved = True
        self.save()

    def check_status(self):
        if self.numOrders == 50 or self.spending >= 500 :
            self.is_vip = True
            self.spending = 0
            self.numOrders = 0

        if self.is_vip :
            if self.rep == 1 :
                self.is_vip = False
                self.rep = 3

        if self.rep == 0:
            self.is_approved = False
            self.deregistered = True
        self.save()


    def __str__(self):
	    return (self.user.first_name + self.user.last_name)


class Staff(models.Model):
    user = models.OneToOneField(User, related_name='staff')
    user_type = models.CharField(max_length =10,choices=type_choices)
    salary = models.FloatField()
    is_approved = models.BooleanField(default=False)
    rep = models.PositiveIntegerField(default=6)
    fired = models.BooleanField(default=False)

    def approve (self):
        self.is_approved = True
        self.save()

    def __str__(self):
        return (self.user.first_name + self.user.last_name)

    def check_status(self):
        if self.rep >= 9 :
            self.salary += 100
            self.rep = 6
        elif self.rep == 3 :
            self.salary -= 100
        elif self.rep <= 0:
            self.fired = True
            self.is_approved = False
        self.save()
