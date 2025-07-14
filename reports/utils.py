from django.db.models import Avg, Max, Min, Count
from django.core.files.base import ContentFile

from exams.models import Exam, StudentScore, ExamSubject
from exams.utils import get_grade_from_score
from students.models import Student
from subjects.models import Subject
from classes.models import ClassLevel, Stream
from institutions.models import Institution

from .models import (
    GeneratedReport, ReportStudentPerformance,
    ReportSubjectBreakdown
)
from .render import render_report_as_pdf
from .ai import generate_summary_for_student, suggest_actions_for_student


def generate_student_academic_summary(student: Student, exam: Exam) -> dict:
    """Compute total, mean, and grade for a given student and exam."""
    scores = StudentScore.objects.filter(
        student=student,
        exam_subject__exam=exam
    ).select_related('exam_subject__subject')

    total = sum(s.score for s in scores)
    count = scores.count()
    mean = round(total / count, 2) if count else 0
    grade = get_grade_from_score(mean, subject=None, institution=exam.institution)

    return {
        "total_marks": total,
        "mean_score": mean,
        "grade": grade
    }


def generate_subject_performance(exam: Exam, subject: Subject, class_level=None, stream=None) -> dict | None:
    """Generate aggregated subject stats for an exam."""
    try:
        exam_subject = ExamSubject.objects.get(exam=exam, subject=subject)
    except ExamSubject.DoesNotExist:
        return None

    scores = StudentScore.objects.filter(exam_subject=exam_subject)
    if class_level:
        scores = scores.filter(student__class_level=class_level)
    if stream:
        scores = scores.filter(student__stream=stream)

    count = scores.count()
    if count == 0:
        return None

    stats = scores.aggregate(
        avg=Avg('score'),
        top=Max('score'),
        low=Min('score')
    )

    passes = scores.filter(score__gte=50).count()
    failures = count - passes

    grade_counts = {}
    for s in scores:
        grade = s.grade or get_grade_from_score(s.score, subject, exam.institution)
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    common_grade = max(grade_counts, key=grade_counts.get)

    return {
        "average_score": round(stats['avg'], 2),
        "top_score": stats['top'],
        "lowest_score": stats['low'],
        "pass_rate": round(passes * 100 / count, 2),
        "failure_rate": round(failures * 100 / count, 2),
        "most_common_grade": common_grade
    }


def generate_grade_distribution(report: GeneratedReport) -> dict:
    """Returns a distribution of grades for a given report."""
    grade_counts = (
        ReportStudentPerformance.objects
        .filter(report=report)
        .values('grade')
        .annotate(count=Count('id'))
    )

    total = sum(item['count'] for item in grade_counts) or 1

    return {
        entry['grade']: {
            'count': entry['count'],
            'percentage': round(entry['count'] * 100 / total, 2)
        }
        for entry in grade_counts
    }


def create_academic_report(
    institution: Institution,
    class_level: ClassLevel,
    stream: Stream,
    exam: Exam,
    term: str,
    year: str,
    generated_by,
    auto: bool = False
) -> GeneratedReport:
    """Create full academic report for a class-stream based on exam."""
    students = Student.objects.filter(
        institution=institution,
        class_level=class_level,
        stream=stream,
        is_active=True
    )

    report = GeneratedReport.objects.create(
        institution=institution,
        report_type='academics',
        title=f"{class_level} {stream} Academic Report - {term} {year}",
        class_level=class_level,
        stream=stream,
        term=term,
        year=year,
        generated_by=generated_by,
        is_auto_generated=auto,
        access_level='guardian'
    )

    performance_data = []
    json_output = []

    for student in students:
        perf = generate_student_academic_summary(student, exam)
        comment = generate_summary_for_student(student=student, exam=exam)
        remedial = suggest_actions_for_student(student=student, exam=exam)

        ReportStudentPerformance.objects.create(
            report=report,
            student=student,
            total_marks=perf['total_marks'],
            mean_score=perf['mean_score'],
            grade=perf['grade'],
            class_level=class_level,
            stream=stream,
            rank=0,
            position_out_of=0,
            comment=comment,
            remedial_suggestion=remedial,
            flagged=perf['grade'] in ['D', 'E']
        )

        performance_data.append((student.id, perf['mean_score']))
        json_output.append({
            "student_id": student.id,
            "name": student.get_full_name(),
            "total_marks": perf['total_marks'],
            "mean_score": perf['mean_score'],
            "grade": perf['grade'],
            "comment": comment,
            "remedial": remedial
        })

    # Rank students
    performance_data.sort(key=lambda x: x[1], reverse=True)
    for i, (student_id, _) in enumerate(performance_data, 1):
        ReportStudentPerformance.objects.filter(report=report, student_id=student_id).update(
            rank=i,
            position_out_of=len(performance_data)
        )

    # Subject breakdown
    for subject in Subject.objects.all():
        stats = generate_subject_performance(exam, subject, class_level, stream)
        if stats:
            ReportSubjectBreakdown.objects.create(
                report=report,
                subject=subject,
                exam=exam,
                class_level=class_level,
                stream=stream,
                **stats
            )

    # Save report
    report.json_data = json_output
    report.ai_summary = f"Generated summary for {len(students)} students across {Subject.objects.count()} subjects."
    report.save()

    try:
        pdf_buffer = render_report_as_pdf(report)
        report.file.save(
            f"{report.title.replace(' ', '_')}.pdf",
            ContentFile(pdf_buffer.getvalue())
        )
    except Exception as e:
        report.ai_summary += f"\n[PDF generation failed: {str(e)}]"

    return report


def get_student_report_card(student: Student, term: str, year: str) -> dict | None:
    """Return report PDF + data for a given student and term."""
    try:
        report = GeneratedReport.objects.filter(
            student_performances__student=student,
            term=term,
            year=year,
            report_type='academics'
        ).latest('date_generated')

        return {
            "pdf": report.file.url if report.file else None,
            "json": report.json_data
        }

    except GeneratedReport.DoesNotExist:
        return None
