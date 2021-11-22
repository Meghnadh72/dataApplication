from django.contrib import admin
from django.urls import path

from simpleDataApp import views

urlpatterns = [
    path("homePage", views.homeScreen),
    path("dataset", views.uploadScreen),
    path("compute", views.computeScreen),
    path("plot", views.plotGraph)
]