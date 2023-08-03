from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'grafxapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('form/', views.graph_form, name='graph_form'),
    path('graph/', views.graph, name='graph'),
]
