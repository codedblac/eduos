# from exams.models import ExamResult
# from exams.utils import get_grade_from_score 
# from ..models import GeneratedReport, ReportStudentPerformance, ReportSubjectBreakdown
# from students.models import Student
# from subjects.models import Subject
# from django.db.models import Avg, Max, Min
# from django.utils import timezone


# def generate_academic_report(term, year, class_level, stream, institution, generated_by=None, access_level='guardian'):
#     """
#     Generate a full academic report for a class/stream in a given term and year.
#     Includes student performance, subject breakdown, and ranks.
#     """
#     title = f"Academic Report: {class_level.name} {stream.name} - {term} {year}"
#     description = f"Performance report for {term} {year} ({class_level.name} {stream.name})"

#     report = GeneratedReport.objects.create(
#         institution=institution,
#         report_type='academics',
#         access_level=access_level,
#         title=title,
#         description=description,
#         generated_by=generated_by,
#         term=term,
#         year=year,
#         class_level=class_level,
#         stream=stream,
#         is_auto_generated=False,
#         ai_summary="",
#         json_data=[]
#     )

#     # Step 1: Fetch all active students in class + stream
#     students = Student.objects.filter(
#         institution=institution,
#         class_level=class_level,
#         stream=stream,
#         is_active=True
#     )

#     student_performance_list = []

#     # Step 2: Collect per-student results and build performance data
#     for student in students:
#         results = ExamResult.objects.filter(
#             student=student,
#             exam__term=term,
#             exam__year=year,
#             exam__class_level=class_level,
#             exam__stream=stream,
#             exam__institution=institution
#         )

#         if not results.exists():
#             continue

#         mean_score = results.aggregate(avg=Avg('score'))['avg'] or 0
#         total_marks = results.aggregate(total=Avg('total_score'))['total'] or 0
#         grade = get_grade_from_score(mean_score, subject=None, institution=institution)

#         student_performance_list.append({
#             'student': student,
#             'total_marks': total_marks,
#             'mean_score': mean_score,
#             'grade': grade
#         })

#     # Step 3: Sort and rank students
#     student_performance_list.sort(key=lambda x: x['mean_score'], reverse=True)
#     total_students = len(student_performance_list)

#     student_reports = []
#     for i, perf in enumerate(student_performance_list):
#         student_reports.append(ReportStudentPerformance(
#             report=report,
#             student=perf['student'],
#             total_marks=perf['total_marks'],
#             mean_score=perf['mean_score'],
#             grade=perf['grade'],
#             rank=i + 1,
#             position_out_of=total_students,
#             class_level=class_level,
#             stream=stream,
#             flagged=perf['grade'] in ['D', 'E']
#         ))

#     ReportStudentPerformance.objects.bulk_create(student_reports)

#     # Step 4: Per-subject breakdown
#     subjects = Subject.objects.filter(
#         institution=institution,
#         classlevelsubject__class_level=class_level
#     ).distinct()

#     subject_breakdowns = []
#     for subject in subjects:
#         results = ExamResult.objects.filter(
#             exam__term=term,
#             exam__year=year,
#             exam__class_level=class_level,
#             exam__stream=stream,
#             exam__institution=institution,
#             subject=subject
#         )

#         if not results.exists():
#             continue

#         stats = results.aggregate(
#             avg=Avg('score'),
#             top=Max('score'),
#             low=Min('score')
#         )

#         total = results.count()
#         passes = results.filter(score__gte=40).count()
#         fails = total - passes

#         grades = results.values_list('grade', flat=True)
#         most_common_grade = max(set(grades), key=grades.count) if grades else None

#         subject_breakdowns.append(ReportSubjectBreakdown(
#             report=report,
#             subject=subject,
#             average_score=round(stats['avg'] or 0, 2),
#             top_score=stats['top'] or 0,
#             lowest_score=stats['low'] or 0,
#             pass_rate=round((passes / total) * 100, 2) if total else 0,
#             failure_rate=round((fails / total) * 100, 2) if total else 0,
#             most_common_grade=most_common_grade,
#             class_level=class_level,
#             stream=stream
#         ))

#     ReportSubjectBreakdown.objects.bulk_create(subject_breakdowns)

#     return report
