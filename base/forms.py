from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host','room_id','participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username','email']