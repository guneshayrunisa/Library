from django.contrib import admin
from .models import StudentExtra, Book, IssuedBook
from datetime import date, timedelta

# StudentExtra 
@admin.register(StudentExtra)
class StudentExtraAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment', 'branch')
    search_fields = ('user__first_name', 'enrollment', 'branch')

# Book 
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'isbn', 'author', 'category_display')
    search_fields = ('name', 'isbn', 'author')
    list_filter = ('category',)

    def category_display(self, obj):
        return obj.get_category_display()
    category_display.short_description = 'Category'

# IssuedBook 
@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issuedate', 'expirydate', 'status', 'approved')  
    list_filter = ('status', 'issuedate', 'approved')  
    search_fields = ('student__user__first_name', 'student__enrollment', 'book__name', 'book__isbn')
    actions = ['approve_issues']

    def save_model(self, request, obj, form, change):
        """
        Admin panelinde kayıt yapılırken tetiklenir.
        Eğer approved=True yapılıyorsa, status'u otomatik 'Issued' yapar.
        """
        if obj.approved and obj.status == 'Pending':
            obj.status = 'Issued'
            # Eğer issuedate boşsa, bugünü ata
            if not obj.issuedate:
                obj.issuedate = date.today()
            # Eğer expirydate boşsa, 15 gün sonrasını ata
            if not obj.expirydate:
                obj.expirydate = date.today() + timedelta(days=15)
        
        super().save_model(request, obj, form, change)

    @admin.action(description="Approve selected book issues")
    def approve_issues(self, request, queryset):
        """
        Toplu onaylama işlemi için action.
        """
        count = 0
        for issue in queryset:
            if not issue.approved:
                issue.approved = True
                issue.status = 'Issued'  # ← BURASI ÖNEMLİ!
                
                # Tarihleri ayarla
                if not issue.issuedate:
                    issue.issuedate = date.today()
                if not issue.expirydate:
                    issue.expirydate = date.today() + timedelta(days=15)
                
                issue.save()
                count += 1
        
        self.message_user(request, f"{count} kitap talebi onaylandı ve kullanıcıya verildi.")