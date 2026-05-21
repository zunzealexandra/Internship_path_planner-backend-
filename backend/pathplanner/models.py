from django.db import models


class Internship(models.Model):
    company = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    skills_needed = models.JSONField(default=list)
    skills_learned = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company", "job_title"]

    def __str__(self) -> str:
        return f"{self.company} - {self.job_title}"
