import os
import sys
import django

# Add the project directory to sys.path so we can import 'config'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Major, TrainingObjective, GraduationRequirement, Course, CourseSupport, IndicatorPoint, ObjectiveSupport

print("Checking database...")
print("Majors:", Major.objects.count())
print("Training Objectives:", TrainingObjective.objects.count())
print("Graduation Requirements:", GraduationRequirement.objects.count())
print("Indicator Points:", IndicatorPoint.objects.count())
print("Courses:", Course.objects.count())
print("Course Supports:", CourseSupport.objects.count())
print("Objective Supports:", ObjectiveSupport.objects.count())

majors = Major.objects.all()
if majors.exists():
    print("\nMajors found:")
    for m in majors:
        print(f"  - {m.name} ({m.code})")
        print(f"    Training Objectives: {TrainingObjective.objects.filter(major=m).count()}")
        print(f"    Graduation Requirements: {GraduationRequirement.objects.filter(major=m).count()}")
        print(f"    Courses: {Course.objects.filter(major=m).count()}")
else:
    print("\nNo majors found in database!")
