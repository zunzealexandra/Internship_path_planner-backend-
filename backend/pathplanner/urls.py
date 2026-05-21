from django.urls import path

from .views import InternshipListView, PlanPathView


urlpatterns = [
    path("internships/", InternshipListView.as_view(), name="internship-list"),
    path("path/", PlanPathView.as_view(), name="plan-path"),
]







