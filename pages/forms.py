from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm



#Creation user form
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = {'username','password1','password2'}    




         
                            

                
            


        






