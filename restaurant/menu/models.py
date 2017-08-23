from django.db import models
from django.core.urlresolvers import reverse
from users import models as userModels
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator



cuisineChoices = (('American','American'),
                    ('Asian','Asian'),
                    ('Indian','Indian'), ('Mexican','Mexican')
                    ,('Italian','Italian')
                        )

reviewChoices = ((1,'1'),
                    (2,'2'),
                    (3,'3'), (4,'4')
                    ,(5,'5')
                        )



class Food(models.Model):
    name = models.CharField(max_length=100,blank=False)
    description = models.CharField(max_length=100,blank=False)
    image = models.ImageField()
    price = models.PositiveIntegerField(blank=False)
    chef = models.ForeignKey(userModels.User)
    cuisine = models.CharField(max_length=100, choices=cuisineChoices)
    numOrdered = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    num_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse ('menu:food',
         kwargs={'food':self.name, 'cuisine':self.cuisine} )

    def addRating (self, rating):
        self.avg_rating = (self.num_reviews * self.avg_rating +
                                    rating) / (self.num_reviews+1)
        self.num_reviews +=1
        if rating >= 3 :
            self.chef.staff.rep += 1
            self.chef.staff.save()
        else:
            self.chef.staff.rep -= 1
            self.chef.staff.save()
        self.save()

class Order(models.Model):
    food = models.ForeignKey(Food)
    customer = models.ForeignKey(userModels.User, related_name='orders')
    status = models.CharField(max_length=10, default='cart')
    delivery = models.ForeignKey(userModels.User,null=True, related_name ='deliveries')
    time_stamp = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1,blank=True)

    def rate(self,quality,delivery):
        self.food.addRating(quality)
        if delivery >= 3 :
            self.delivery.staff.rep += 1
            self.delivery.staff.save()
        else:
            self.delivery.staff.rep -= 1
            self.delivery.staff.save()
        self.save()

    def __str__(self):
        return self.food.name



class Review(models.Model):
    foodQuality = models.CharField(max_length=100,default='')
    qValue = models.PositiveIntegerField(default=0,
                        validators=[MaxValueValidator(5)], choices=reviewChoices)
    customer = models.ForeignKey(userModels.User, blank=True, null=True)
    order = models.ForeignKey(Order, null=True, blank=True, related_name='reviews')
    deliverySpeed = models.CharField(max_length=100,default='')
    dValue = models.PositiveIntegerField(default=0,
        validators=[MaxValueValidator(5)], choices=reviewChoices)

    def execute(self):
        self.order.rate(self.qValue,self.dValue)




class Message (models.Model):
    target = models.ForeignKey(userModels.User, related_name='inbox')
    source = models.ForeignKey(userModels.User, related_name='outbox')
    reason = models.CharField(max_length=100)
    message_type = models.CharField(max_length=10)
    status = models.CharField(max_length = 10, default='unhandled')
