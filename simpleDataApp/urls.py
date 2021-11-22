from django.contrib import admin
from django.urls import path

from simpleDataApp import views

urlpatterns = [
    path("homePage", views.homeScreen),
    path("dataset", views.uploadScreen),    # This API Corresponds to Both GET AND POST Requests
    path("compute", views.computeScreen),   # THis API Corresponds to 3rd API in the Project Specifications
    path("plot", views.plotGraph)           # This API corresponds to 4th API "plot/?id/ ....."
]