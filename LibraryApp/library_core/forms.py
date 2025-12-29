from django import forms
from django.contrib.auth.models import User
from . import models

class BookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['name', 'isbn', 'author', 'category']

class StudentUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

class StudentExtraForm(forms.ModelForm):
    class Meta:
        model = models.StudentExtra
        fields = ['branch']  # enrollment kaldırıldı

class IssuedBookForm(forms.ModelForm):
    class Meta:
        model = models.IssuedBook
        exclude = ['issuedate']  # issuedate otomatik ayarlanır, formda gösterilmez
        widgets = {
            'expirydate': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        }
