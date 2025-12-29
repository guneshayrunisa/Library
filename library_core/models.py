from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class StudentExtra(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrollment = models.CharField(max_length=40, unique=True, blank=True)
    branch = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.user.first_name} [{self.enrollment}]"

    def save(self, *args, **kwargs):
        if not self.enrollment:
            last_student = StudentExtra.objects.order_by('-id').first()
            if last_student and last_student.enrollment.isdigit():
                self.enrollment = str(int(last_student.enrollment) + 1)
            else:
                self.enrollment = '1000'
        super().save(*args, **kwargs)

class Book(models.Model):
    catchoice = [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
    ]
    name = models.CharField(max_length=50)
    isbn = models.BigIntegerField()
    author = models.CharField(max_length=50)
    category = models.CharField(max_length=30, choices=catchoice, default='education')

    def __str__(self):
        return f"{self.name} [{self.isbn}]"

def get_expiry():
    return datetime.today() + timedelta(days=30)

class IssuedBook(models.Model):
    student = models.ForeignKey(StudentExtra, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    issuedate = models.DateField(auto_now=True)
    expirydate = models.DateField(default=get_expiry)
    approved = models.BooleanField(default=False)

    statuschoice = [
        ('Pending', 'Pending'),  # Yeni eklenen durum
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
    ]
    status = models.CharField(max_length=20, choices=statuschoice, default='Pending')

    def __str__(self):
        return f"{self.student.enrollment} - {self.book.name}"
