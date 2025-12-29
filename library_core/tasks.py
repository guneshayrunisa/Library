from celery import shared_task
from .models import IssuedBook
from django.core.mail import send_mail
from django.conf import settings
from datetime import date

@shared_task
def send_reminder_emails():
    today = date.today()
    # Onaylanmış ve expirydate dolu olan kitaplar
    books = IssuedBook.objects.filter(approved=True).exclude(expirydate__isnull=True)

    sent_count = 0

    for book in books:
        days_left = (book.expirydate - today).days
        # Süresi bugün veya yarın dolacak olanlara mail gönder (dilersen sadece 0 yapabilirsin)
        if days_left in (0, 1):
            student_email = book.student.user.email
            student_name = book.student.user.first_name
            book_name = book.book.name

            try:
                send_mail(
                    subject='Reminder: Book due soon',
                    message=(
                        f"Dear {student_name},\n\n"
                        f"The book '{book_name}' is due {'today' if days_left == 0 else 'tomorrow'}. "
                        "Please return it on time to avoid penalties."
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[student_email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                # İstersen burada logging yapabilirsin
                print(f"Failed to send mail to {student_email}: {e}")

    return f"{sent_count} reminder emails sent."
