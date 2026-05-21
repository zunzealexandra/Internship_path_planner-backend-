from rest_framework import serializers

from .models import Internship


class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = [
            "id",
            "company",
            "job_title",
            "location",
            "job_type",
            "experience",
            "skills_needed",
            "skills_learned",
        ]







