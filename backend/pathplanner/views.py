from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .astar import PathPlanner
from .models import Internship
from .serializers import InternshipSerializer
from .utils import normalize_skills


class InternshipListView(APIView):
    def get(self, request):
        queryset = Internship.objects.all()
        location = request.query_params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)
        serializer = InternshipSerializer(queryset, many=True)
        return Response(serializer.data)


class PlanPathView(APIView):
    def post(self, request):
        skills_input = request.data.get("skills", [])
        target_role = request.data.get("target_role")
        location = request.data.get("location")

        if not target_role or not location:
            return Response(
                {"error": "target_role and location are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_skills = normalize_skills(skills_input)
        internships = Internship.objects.filter(location__icontains=location)
        if not internships.exists():
            return Response(
                {"error": "No internships found for that location."},
                status=status.HTTP_404_NOT_FOUND,
            )

        planner = PathPlanner(internships)
        result = planner.plan(normalized_skills, target_role)
        payload = {
            "start_skills": normalized_skills,
            "location": location,
            **result,
        }
        return Response(payload)
