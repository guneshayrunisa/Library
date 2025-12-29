from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login  
from datetime import date, timedelta
from django.contrib import messages
from . import forms, models
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Book, IssuedBook

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

            return redirect('studentlogin')  # doğru yönlendirme
  

    return render(request, 'library/studentsignup.html', context=mydict)

# Öğrenci mi kontrolü
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

# Giriş sonrası yönlendirme
def afterlogin_view(request):
    if request.user.groups.filter(name='STUDENT').exists():
        student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
        
        if not student:
            messages.error(request, 'Öğrenci profili bulunamadı.')
            return redirect('home_view')
        
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
    messages.success(request, "Kitap başarıyla iade edildi.")
    return redirect('viewissuedbookbystudent')

# Öğrenciye ait ödünç alınan kitapları görüntüleme
@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"Session key: {request.session.session_key}")
    
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
    
    if not student:
        messages.error(request, 'Öğrenci profili bulunamadı. Lütfen yöneticiyle iletişime geçin.')
        return redirect('home_view')
    
    # ONAYLANMIŞ VE AKTİF KİTAPLAR (Issued durumunda)
    issuedbooks = models.IssuedBook.objects.filter(
        student=student, 
        approved=True, 
        status='Issued'
    ).select_related('book')

    # ONAY BEKLEYEN KİTAP İSTEKLERİ
    pendingbooks = models.IssuedBook.objects.filter(
        student=student, 
        approved=False, 
        status='Pending'
    ).select_related('book')

    # İstek gönderilmiş veya ödünç alınmış kitapların ISBN'leri
    requested_books_isbn = models.IssuedBook.objects.filter(
        student=student,
        status__in=['Pending', 'Issued']
    ).values_list('book__isbn', flat=True)

    # Tüm kitaplar içinden istek gönderilmiş kitapları çıkar
    available_books = models.Book.objects.exclude(isbn__in=requested_books_isbn)

    # Liste 1: Alınan kitapların bilgileri
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
        'pendingbooks': pendingbooks,
        'pending_count': pendingbooks.count(),
        'issued_count': issuedbooks.count(),
    })

# Öğrenci giriş sayfası
def studentlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Kullanıcı adı ve şifreyi kontrol etme
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('afterlogin')  # Başarılı giriş sonrası yönlendirme
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre')
            return redirect('studentlogin')  # Giriş başarısızsa tekrar giriş sayfasına yönlendirme

    return render(request, 'library/studentlogin.html')


# Kitap talep etme
@login_required(login_url='studentlogin')
def issuebook(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn2')
        enrollment = request.POST.get('enrollment2')

        student = models.StudentExtra.objects.filter(enrollment=enrollment).first()
        book = models.Book.objects.filter(isbn=isbn).first()

        if student and book:
            # Aynı kitap zaten istenmiş mi?
            existing_request = models.IssuedBook.objects.filter(
                student=student,
                book=book,
                status__in=['Pending', 'Issued']
            ).exists()

            if existing_request:
                messages.warning(request, 'Bu kitabı zaten talep ettiniz veya ödünç aldınız.')
                return redirect('viewissuedbookbystudent')

            # Aktif kitap sayısı kontrolü
            active_books_count = models.IssuedBook.objects.filter(
                student=student,
                status__in=['Pending', 'Issued']
            ).count()

            if active_books_count >= 3:
                messages.warning(request, 'Aynı anda en fazla 3 kitap talep edebilirsiniz.')
                return redirect('viewissuedbookbystudent')

            # Yeni kitap isteği oluştur
            models.IssuedBook.objects.create(
                student=student,
                book=book,
                approved=False,
                status='Pending',
                issuedate=date.today(),
                expirydate=date.today() + timedelta(days=15)
            )
            messages.success(request, 'Kitap talebiniz başarıyla gönderildi.')
        else:
            messages.error(request, 'Geçersiz öğrenci veya kitap.')

        return redirect('viewissuedbookbystudent')
    else:
        return redirect('viewissuedbookbystudent')
    

@require_http_methods(["GET"])
def api_books(request):
    books = list(
        Book.objects.all().values("id", "name", "isbn", "author", "category")
    )
    return JsonResponse({"count": len(books), "results": books})

@csrf_exempt
@require_http_methods(["POST"])
def api_issue_book(request):
    """
    Body JSON örnek:
    {
      "student_id": 1,
      "book_id": 2
    }
    """
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
        student_id = data.get("student_id")
        book_id = data.get("book_id")
        if not student_id or not book_id:
            return JsonResponse({"error": "student_id ve book_id zorunlu"}, status=400)

        obj = IssuedBook.objects.create(student_id=student_id, book_id=book_id)
        return JsonResponse({"message": "issued", "issued_id": obj.id}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# Test için basit view
def simple_test(request):
    return HttpResponse("Hello, Render!")