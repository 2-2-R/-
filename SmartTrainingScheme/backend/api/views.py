# backend/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Major, GraduationRequirement, Course, CourseSupport, IndicatorPoint
from decimal import Decimal

class SchemeVisualizeView(APIView):
    def get(self, request):
        major = Major.objects.first()
        if not major:
            return Response({"error": "No data found in database."}, status=404)

        reqs = GraduationRequirement.objects.filter(major=major).order_by('sequence')
        req_data = [{"id": r.sequence, "name": r.content} for r in reqs]

        courses = Course.objects.filter(major=major).prefetch_related(
            'supports__indicator__requirement', 
            'prerequisites'
        )
        
        course_data = []
        for c in courses:
            supports = []
            for s in c.supports.all():
                w = float(s.weight)
                level = 'L'
                if w >= 0.5:
                    level = 'H'
                elif w >= 0.3:
                    level = 'M'
                
                supports.append({
                    "req": s.indicator.requirement.sequence,
                    "level": level
                })
            
            course_data.append({
                "code": c.code,
                "name": c.name,
                "category": c.category or "Other",
                "semester": c.semester or 1,
                "credits": float(c.credits or 0),
                "supports": supports,
                "prereqs": [p.code for p in c.prerequisites.all()]
            })

        return Response({
            "major": major.name,
            "requirements": req_data,
            "courses": course_data
        })


class MatrixHeatmapView(APIView):
    def get(self, request):
        major = Major.objects.first()
        if not major:
            return Response({"error": "No data found in database."}, status=404)

        indicator_points = IndicatorPoint.objects.filter(
            requirement__major=major
        ).select_related('requirement').order_by('requirement__sequence', 'sequence')
        
        indicator_data = []
        for ip in indicator_points:
            indicator_data.append({
                "id": ip.id,
                "number": f"{ip.requirement.sequence}.{ip.sequence}",
                "content": ip.content,
                "requirement_id": ip.requirement.id
            })

        courses = Course.objects.filter(major=major).order_by('category', 'semester', 'name')
        
        course_data = []
        for c in courses:
            course_data.append({
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "category": c.category or "Other",
                "semester": c.semester or 1,
                "credits": float(c.credits or 0)
            })

        support_matrix = CourseSupport.objects.filter(
            course__major=major
        ).select_related('course', 'indicator')
        
        support_data = []
        for s in support_matrix:
            support_data.append({
                "course_id": s.course.id,
                "indicator_point_id": s.indicator.id,
                "weight": float(s.weight)
            })

        return Response({
            "major": major.name,
            "indicator_points": indicator_data,
            "courses": course_data,
            "support_matrix": support_data
        })
