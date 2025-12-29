from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from datetime import date
from django.contrib import messages
from . import forms, models
from django.db.models import Q

# Ana sayfa
def home_view(request):
    return render(request, "library/index.html")

# Öğrenci giriş sayfasına yönlendirme
def studentclick_view(request):
    return render(request, "library/studentclick.html")

# Öğrenci kayıt işlemi
def studentsignup_view(request):
    form1 = forms.StudentUserForm()
    form2 = forms.StudentExtraForm()
    mydict = {'form1': form1, 'form2': form2}

    if request.method == 'POST':
        form1 = forms.StudentUserForm(request.POST)
        form2 = forms.StudentExtraForm(request.POST)

        if form1.is_valid() and form2.is_valid():
            user = form1.save(commit=False)
            user.set_password(user.password)
            user.save()

            f2 = form2.save(commit=False)
            f2.user = user
            f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

            return HttpResponseRedirect('studentlogin')

    return render(request, 'library/studentsignup.html', context=mydict)

# Öğrenci mi kontrolü
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

# Giriş sonrası yönlendirme
def afterlogin_view(request):
    if request.user.groups.filter(name='STUDENT').exists():
        student = get_object_or_404(models.StudentExtra, user=request.user)
        all_books = models.Book.objects.all()

        context = {
            'student': student,
            'user': request.user,
            'all_books': all_books,
        }
        return render(request, 'library/studentafterlogin.html', context)

    elif request.user.is_superuser:
        return redirect('/admin')

    else:
        return redirect('home_view')

# Kitap iade işlemi
@login_required(login_url='studentlogin')
def returnbook(request, id):
    issued_book = get_object_or_404(models.IssuedBook, pk=id)
    issued_book.status = "Returned"
    issued_book.save()
    messages.success(request, "Book returned successfully.")
    return redirect('viewissuedbookbystudent')

# Öğrenciye ait ödünç alınan kitapları görüntüleme
@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
    
    # Sadece onaylanmış ve aktif kitaplar
    issuedbooks = models.IssuedBook.objects.filter(student=student, approved=True, status='Issued')

    # Onay bekleyen kitap istekleri
    pendingbooks = models.IssuedBook.objects.filter(student=student, approved=False, status='Pending')

    # İstek gönderilmiş kitapların ISBN'leri (onaylı veya beklemede)
    requested_books_isbn = models.IssuedBook.objects.filter(student=student).values_list('book__isbn', flat=True)

    # Tüm kitaplar içinden istek gönderilmiş kitapları çıkar
    available_books = models.Book.objects.exclude(isbn__in=requested_books_isbn)

    li1 = []
    li2 = []

    for ib in issuedbooks:
        book = ib.book
        t1 = (request.user, student.enrollment, student.branch, book.name, book.author)
        li1.append(t1)

        issdate = f"{ib.issuedate.day}-{ib.issuedate.month}-{ib.issuedate.year}"
        expdate = f"{ib.expirydate.day}-{ib.expirydate.month}-{ib.expirydate.year}"

        days = (date.today() - ib.issuedate).days
        fine = 0
        if days > 15:
            fine = (days - 15) * 10

        t2 = (issdate, expdate, fine, ib.status, ib.id)
        li2.append(t2)

    return render(request, 'library/viewissuedbookbystudent.html', {
        'li1': li1,
        'li2': li2,
        'all_books': available_books,
        'student': student,
        'pendingbooks': pendingbooks  # İstersen template'te kullanabilirsin
    })

# Kitap talep etme
@login_required(login_url='studentlogin')
def issuebook(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn2')
        enrollment = request.POST.get('enrollment2')

        student = models.StudentExtra.objects.filter(enrollment=enrollment).first()
        book = models.Book.objects.filter(isbn=isbn).first()

        if student and book:
            # Aynı kitap zaten istenmiş mi? (onaylı veya beklemede)
            existing_request = models.IssuedBook.objects.filter(
                student=student,
                book=book,
                status__in=['Pending', 'Issued']
            ).exists()

            if existing_request:
                messages.warning(request, 'You have already requested or borrowed this book.')
                return redirect('viewissuedbookbystudent')

            # Aktif kitap sayısı (onaylı veya beklemede)
            active_books_count = models.IssuedBook.objects.filter(
                student=student,
                status__in=['Pending', 'Issued']
            ).count()

            if active_books_count >= 3:
                messages.warning(request, 'You cannot request more than 3 books at a time.')
                return redirect('viewissuedbookbystudent')

            # Yeni kitap isteği oluştur
            models.IssuedBook.objects.create(
                student=student,
                book=book,
                approved=False,
                status='Pending'
            )
            messages.success(request, 'Book request submitted successfully.')
        else:
            messages.error(request, 'Invalid student or book.')

        return redirect('viewissuedbookbystudent')

    else:
        return redirect('viewissuedbookbystudent')
# views.py içinde
from django.http import HttpResponse

def simple_test(request):
    return HttpResponse("Hello, Render!")
