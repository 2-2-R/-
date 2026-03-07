# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Major, TrainingObjective, GraduationRequirement, 
    ObjectiveSupport, IndicatorPoint, Course, CourseSupport
)

output_file = 'verification_result.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("Database Data Verification Report\n")
    f.write("=" * 80 + "\n\n")
    
    # Check majors
    f.write("[1. Major Information]\n")
    majors = Major.objects.all()
    f.write(f"Total majors in database: {majors.count()}\n")
    for major in majors:
        f.write(f"  - {major.name} ({major.code})\n")
    
    # Find IoT major
    iot_major = Major.objects.filter(name__contains="ÎïÁªÍø").first()
    if not iot_major:
        f.write("\nERROR: IoT Engineering major not found!\n")
        print("ERROR: IoT Engineering major not found!")
        sys.exit(1)
    
    f.write(f"\nFound major: {iot_major.name} ({iot_major.code})\n")
    
    # Check training objectives
    f.write("\n[2. Training Objectives]\n")
    objectives = TrainingObjective.objects.filter(major=iot_major)
    f.write(f"Total training objectives: {objectives.count()}\n")
    for obj in objectives:
        f.write(f"  Objective {obj.sequence}: {obj.content[:50]}...\n")
    
    # Check graduation requirements
    f.write("\n[3. Graduation Requirements]\n")
    requirements = GraduationRequirement.objects.filter(major=iot_major)
    f.write(f"Total graduation requirements: {requirements.count()}\n")
    for req in requirements:
        f.write(f"  Requirement {req.sequence}: {req.content[:50]}...\n")
        indicators = IndicatorPoint.objects.filter(requirement=req)
        f.write(f"    Contains {indicators.count()} indicator points\n")
        for ind in indicators:
            f.write(f"       Indicator {req.sequence}.{ind.sequence} (weight: {ind.weight})\n")
    
    # Check objective support relations
    f.write("\n[4. Objective Support Relations]\n")
    obj_supports = ObjectiveSupport.objects.filter(requirement__major=iot_major)
    f.write(f"Total objective support relations: {obj_supports.count()}\n")
    if obj_supports.count() > 0:
        f.write("  Examples:\n")
        for support in list(obj_supports[:5]):
            f.write(f"  - Req{support.requirement.sequence} -> Obj{support.objective.sequence} (weight: {support.weight})\n")
    
    # Check courses
    f.write("\n[5. Courses]\n")
    courses = Course.objects.filter(major=iot_major)
    f.write(f"Total courses: {courses.count()}\n")
    if courses.count() > 0:
        f.write("  Example courses:\n")
        for course in list(courses[:10]):
            f.write(f"  - {course.name} ({course.code}) - {course.credits} credits\n")
    
    # Check course support relations
    f.write("\n[6. Course Support Relations]\n")
    course_supports = CourseSupport.objects.filter(course__major=iot_major)
    f.write(f"Total course support relations: {course_supports.count()}\n")
    if course_supports.count() > 0:
        f.write("  Examples:\n")
        for support in list(course_supports[:10]):
            f.write(f"  - {support.course.name} -> Indicator {support.indicator.requirement.sequence}.{support.indicator.sequence} (weight: {support.weight})\n")
    
    # Data integrity check
    f.write("\n[7. Data Integrity Check]\n")
    f.write(f"Majors: {majors.count()}\n")
    f.write(f"Training Objectives: {objectives.count()}\n")
    f.write(f"Graduation Requirements: {requirements.count()}\n")
    f.write(f"Indicator Points: {IndicatorPoint.objects.filter(requirement__major=iot_major).count()}\n")
    f.write(f"Courses: {courses.count()}\n")
    f.write(f"Objective Support Relations: {obj_supports.count()}\n")
    f.write(f"Course Support Relations: {course_supports.count()}\n")
    
    # Final verdict
    if (objectives.count() > 0 and requirements.count() > 0 and 
        courses.count() > 0 and course_supports.count() > 0):
        f.write("\n" + "=" * 80 + "\n")
        f.write("SUCCESS: IoT Engineering data has been imported successfully!\n")
        f.write("=" * 80 + "\n")
        print("SUCCESS: Data verification complete. Check verification_result.txt for details.")
    else:
        f.write("\n" + "=" * 80 + "\n")
        f.write("WARNING: Data is incomplete, may need to re-import.\n")
        f.write("=" * 80 + "\n")
        print("WARNING: Data is incomplete. Check verification_result.txt for details.")

print(f"Verification report saved to: {output_file}")
