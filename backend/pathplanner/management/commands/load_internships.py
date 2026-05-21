import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pathplanner.models import Internship
from pathplanner.utils import normalize_skills


class Command(BaseCommand):
    help = "Load internships from a CSV file into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            help="Path to internships CSV. Defaults to the root internships.csv file.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing internship rows before loading.",
        )

    def handle(self, *args, **options):
        csv_path = options.get("path")
        reset = options.get("reset")

        if not csv_path:
            csv_path = Path(settings.BASE_DIR).parent / "internships.csv"
        else:
            csv_path = Path(csv_path)

        if not csv_path.exists():
            self.stderr.write(f"CSV file not found: {csv_path}")
            return

        if reset:
            Internship.objects.all().delete()
            self.stdout.write("Cleared existing internships.")

        created, updated = 0, 0
        with csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row.get("Company"):
                    continue

                skills_needed = normalize_skills(row.get("Skills Needed", ""))
                skills_learned = normalize_skills(row.get("Skills Learned", ""))
                defaults = {
                    "job_type": row.get("Job Type", "").strip(),
                    "experience": row.get("Experience", "").strip(),
                    "skills_needed": skills_needed,
                    "skills_learned": skills_learned,
                }

                obj, was_created = Internship.objects.update_or_create(
                    company=row.get("Company", "").strip(),
                    job_title=row.get("Job Title", "").strip(),
                    location=row.get("Location", "").strip(),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            f"Loaded internships from {csv_path}. Created: {created}, Updated: {updated}."
        )







