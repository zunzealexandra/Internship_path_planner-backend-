from django.contrib import admin

from .models import Internship


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("company", "job_title", "location", "job_type", "experience")
    search_fields = ("company", "job_title", "location", "skills_needed", "skills_learned")
    list_filter = ("location", "job_type", "experience")
