from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import IssuedBook

@receiver(post_save, sender=IssuedBook)
def send_approval_email(sender, instance, created, **kwargs):
    # Onay durumu True olduysa ve bu yeni bir kayıt değilse (created=False)
    if instance.approved and not created:
        student_email = instance.student.user.email
        book_name = instance.book.name
        student_name = instance.student.user.first_name

        try:
            send_mail(
                subject='Book Issue Approved',
                message=(
                    f"Dear {student_name}, your request to borrow the book '{book_name}' has been approved. "
                    f"You can now collect it from the library. Please note that you have 30 days to return the book. "
                    
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student_email],
                fail_silently=False,
            )
            print(f"Email sent to {student_email}")
        except Exception as e:
            print(f"Failed to send email to {student_email}: {e}")

