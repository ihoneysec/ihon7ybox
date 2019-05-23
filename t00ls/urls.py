from django.urls import path
from . import views
from django.views.generic.base import RedirectView

app_name = 't00ls'
urlpatterns = [
    path('', views.integratedquery, name='integratedquery'),
    path('index/', views.index, name='index'),
    path('integratedquery/', views.integratedquery, name='integratedquery'),
    path('favicon.ico', RedirectView.as_view(url='static/t00ls/favicon.ico'))
]
