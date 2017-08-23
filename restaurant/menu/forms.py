from django import forms
from .models import Food, Review, Message


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ('name','description','image', 'cuisine', 'price')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = ('foodQuality','qValue','deliverySpeed','dValue')

        labels = {'foodQuality':'Quality','qValue':'Rating',
                    'deliverySpeed':'Delivery','dValue':'Rating'}


feedbackCHOICES = ( ('Complaint','Complaint'),
            ('Complement','Complement')
            )

serviceCHOICES = ( ('food','Food Quality'),
            ('delivery','Delivery Speed')
            )

class MessageForm(forms.Form):
    content = forms.CharField(max_length=100)
    feedback = forms.ChoiceField(widget=forms.RadioSelect,
                    choices=feedbackCHOICES)
    service = forms.ChoiceField(widget=forms.RadioSelect,
                    choices=serviceCHOICES)
