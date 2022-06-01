"""kawasanku URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from http.client import HTTPResponse
from django.contrib import admin
from django.urls import path
from kawasanku import views
from django.http import HttpResponse



urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', views.TestJSON.as_view(), name='Test JSON'),
    path('snapshot/', views.Snapshot.as_view(), name='Snapshot'),
    path('doughnut/', views.DoughnutsJSON.as_view(), name='Doughnut'),
    path('pyramid/', views.PyramidJSON.as_view(), name='Pyramid'),
    path('links/', views.StaticJSON.as_view(), name='Static'),
    path('geo/', views.GeoJSON.as_view(), name='Geo'),
    path('dropdown/', views.DropdownJSON.as_view(), name='Dropdown'),
    path('jitter/', views.JitterJSON.as_view(), name='Jitter'),
    path('area-type/', views.AreaJSON.as_view(), name='Area'),
    path('reqbin-verify.txt', views.TestJSON.as_view())
]