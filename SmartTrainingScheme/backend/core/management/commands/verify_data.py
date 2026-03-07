from django.core.management.base import BaseCommand
from core.models import (
    Major, TrainingObjective, GraduationRequirement, 
    ObjectiveSupport, IndicatorPoint, Course, CourseSupport
)

class Command(BaseCommand):
    help = 'Verify if IoT Engineering data has been imported'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("Database Data Verification Report")
        self.stdout.write("=" * 80)
        
        # Check majors
        self.stdout.write("\n[1. Major Information]")
        majors = Major.objects.all()
        self.stdout.write(f"Total majors in database: {majors.count()}")
        for major in majors:
            self.stdout.write(f"  - {major.name} ({major.code})")
        
        # Find IoT major
        iot_major = majors.first()
        if not iot_major:
            self.stdout.write(self.style.ERROR("\nERROR: No major found!"))
            return
        
        self.stdout.write(f"\nFound major: {iot_major.name} ({iot_major.code})")
        
        # Check training objectives
        self.stdout.write("\n[2. Training Objectives]")
        objectives = TrainingObjective.objects.filter(major=iot_major)
        self.stdout.write(f"Total training objectives: {objectives.count()}")
        for obj in objectives[:5]:
            self.stdout.write(f"  Objective {obj.sequence}: {obj.content[:50]}...")
        
        # Check graduation requirements
        self.stdout.write("\n[3. Graduation Requirements]")
        requirements = GraduationRequirement.objects.filter(major=iot_major)
        self.stdout.write(f"Total graduation requirements: {requirements.count()}")
        for req in requirements[:5]:
            self.stdout.write(f"  Requirement {req.sequence}: {req.content[:50]}...")
            indicators = IndicatorPoint.objects.filter(requirement=req)
            self.stdout.write(f"    Contains {indicators.count()} indicator points")
        
        # Check objective support relations
        self.stdout.write("\n[4. Objective Support Relations]")
        obj_supports = ObjectiveSupport.objects.filter(requirement__major=iot_major)
        self.stdout.write(f"Total objective support relations: {obj_supports.count()}")
        
        # Check courses
        self.stdout.write("\n[5. Courses]")
        courses = Course.objects.filter(major=iot_major)
        self.stdout.write(f"Total courses: {courses.count()}")
        if courses.count() > 0:
            self.stdout.write("  Example courses:")
            for course in courses[:5]:
                self.stdout.write(f"  - {course.name} ({course.code}) - {course.credits} credits")
        
        # Check course support relations
        self.stdout.write("\n[6. Course Support Relations]")
        course_supports = CourseSupport.objects.filter(course__major=iot_major)
        self.stdout.write(f"Total course support relations: {course_supports.count()}")
        
        # Data integrity check
        self.stdout.write("\n[7. Data Integrity Summary]")
        self.stdout.write(f"Majors: {majors.count()}")
        self.stdout.write(f"Training Objectives: {objectives.count()}")
        self.stdout.write(f"Graduation Requirements: {requirements.count()}")
        self.stdout.write(f"Indicator Points: {IndicatorPoint.objects.filter(requirement__major=iot_major).count()}")
        self.stdout.write(f"Courses: {courses.count()}")
        self.stdout.write(f"Objective Support Relations: {obj_supports.count()}")
        self.stdout.write(f"Course Support Relations: {course_supports.count()}")
        
        # Final verdict
        if (objectives.count() > 0 and requirements.count() > 0 and 
            courses.count() > 0 and course_supports.count() > 0):
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.SUCCESS("SUCCESS: Data has been imported successfully!"))
            self.stdout.write("=" * 80)
        else:
            self.stdout.write("\n" + "=" * 80)
            self.stdout.write(self.style.WARNING("WARNING: Data is incomplete, may need to re-import."))
            self.stdout.write("=" * 80)
