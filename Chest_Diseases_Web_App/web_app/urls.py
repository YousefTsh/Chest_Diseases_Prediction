from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login,name = 'login'),
    path('chest/',views.chestPage,name= 'chest'),
    path('breast_cancer/',views.breastPage,name='breast'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('logout/',views.logout,name='logout'),
    path('breast_report/',views.breast_report,name='breast_report'),
    path('chest_report/',views.chest_report,name='chest_report'),
    path('dashboard/<str:pk>/',views.dashboard,name='dashboard'),
    path('ct_scans/',views.ct_scans,name='ct'),
    path('ct_report/',views.ct_report,name='ct_rep')
]