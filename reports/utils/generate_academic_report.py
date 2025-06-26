from exams.models import ExamResult
from exams.utils import get_grade  # Your custom grade utility
from ..models import GeneratedReport, ReportStudentPerformance, ReportSubjectBreakdown
from students.models import Student
from subjects.models import Subject
from django.db.models import Avg, Max, Min
from django.utils import timezone


def generate_academic_report(term, year, class_level, stream, institution, generated_by=None, access_level='guardian'):
    """
    Generate a full academic report for a class/stream in a given term and year.
    """

    title = f"Academic Report: {class_level.name} {stream.name} - {term} {year}"
    description = f"Performance report for {term} {year} ({class_level.name} {stream.name})"

    report = GeneratedReport.objects.create(
        institution=institution,
        report_type='academics',
        access_level=access_level,
        title=title,
        description=description,
        generated_by=generated_by,
        term=term,
        year=year,
        class_level=class_level,
        stream=stream,
    )

    # Step 1: All students in the stream
    students = Student.objects.filter(
        institution=institution,
        class_level=class_level,
        stream=stream
    )

    # Step 2: Collect per-student results
    student_performance_list = []

    for student in students:
        results = ExamResult.objects.filter(
            student=student,
            exam__term=term,
            exam__year=year,
            exam__class_level=class_level,
            exam__stream=stream,
            exam__institution=institution
        )

        if not results.exists():
            continue

        total_marks = results.aggregate(total=Avg('total_score'))['total'] or 0
        mean_score = total_marks  # Total marks across all subjects
        grade = get_grade(mean_score)

        student_performance_list.append({
            'student': student,
            'total_marks': total_marks,
            'mean_score': mean_score,
            'grade': grade,
        })

    # Step 3: Rank students and create ReportStudentPerformance records
    student_performance_list.sort(key=lambda x: x['mean_score'], reverse=True)
    total_students = len(student_performance_list)

    ReportStudentPerformance.objects.bulk_create([
        ReportStudentPerformance(
            report=report,
            student=perf['student'],
            total_marks=perf['total_marks'],
            mean_score=perf['mean_score'],
            grade=perf['grade'],
            rank=i + 1,
            position_out_of=total_students,
            class_level=class_level,
            stream=stream
        )
        for i, perf in enumerate(student_performance_list)
    ])

    # Step 4: Per-subject breakdown
    subjects = Subject.objects.filter(
        institution=institution,
        classlevelsubject__class_level=class_level
    ).distinct()

    subject_breakdowns = []
    for subject in subjects:
        results = ExamResult.objects.filter(
            exam__term=term,
            exam__year=year,
            exam__class_level=class_level,
            exam__stream=stream,
            subject=subject,
            exam__institution=institution
        )

        if not results.exists():
            continue

        avg = results.aggregate(Avg('score'))['score__avg'] or 0
        top = results.aggregate(Max('score'))['score__max'] or 0
        low = results.aggregate(Min('score'))['score__min'] or 0

        total = results.count()
        passes = results.filter(score__gte=40).count()
        fails = total - passes

        grades = results.values_list('grade', flat=True)
        most_common_grade = max(set(grades), key=grades.count) if grades else None

        subject_breakdowns.append(
            ReportSubjectBreakdown(
                report=report,
                subject=subject,
                average_score=avg,
                top_score=top,
                lowest_score=low,
                pass_rate=(passes / total) * 100 if total else 0,
                failure_rate=(fails / total) * 100 if total else 0,
                most_common_grade=most_common_grade,
                class_level=class_level,
                stream=stream
            )
        )

    ReportSubjectBreakdown.objects.bulk_create(subject_breakdowns)

    return report
