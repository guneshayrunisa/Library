from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from library_core import views
from django.contrib.auth.views import LoginView, LogoutView
from library_core.views import simple_test
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('test/', simple_test),
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home_view'),
    path('issuebook/', views.issuebook, name='issuebook'),
    path('studentclick/', views.studentclick_view, name='studentclick'),
    path('studentsignup/', views.studentsignup_view, name='studentsignup'),
    path('studentlogin/', views.studentlogin_view, name='studentlogin'),  
    path('returnbook/<int:id>/', views.returnbook, name='returnbook'),
    path('logout/', LogoutView.as_view(next_page='studentlogin'), name='logout'), 
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('viewissuedbookbystudent/', views.viewissuedbookbystudent, name='viewissuedbookbystudent'),
    path('accounts/', include('django.contrib.auth.urls')),
    path("", include("library_core.urls")),
]