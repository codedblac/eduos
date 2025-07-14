# exams/render.py

import os
import tempfile
import subprocess
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.text import slugify
from exams.models import Exam
from assessments.models import Question


def generate_latex_exam(exam: Exam, include_answers=False, randomize=False):
    """
    Generate a LaTeX string for the exam.
    If include_answers is True, answers are included (teacher version).
    """
    context = {
        "exam": exam,
        "subjects": [],
        "include_answers": include_answers
    }

    for subject in exam.subjects.all():
        questions = Question.objects.filter(
            assessment__title__icontains=exam.name,
            subject=subject.subject
        )
        if randomize:
            questions = questions.order_by('?')

        context["subjects"].append({
            "subject": subject.subject,
            "questions": questions
        })

    try:
        return render_to_string("exams/templates/exam_latex.tex", context)
    except Exception as e:
        raise RuntimeError(f"LaTeX template rendering failed: {e}")


def compile_latex_to_pdf(latex_str: str, output_filename: str = None) -> str:
    """
    Compile LaTeX content into a PDF using pdflatex.
    Returns the file path of the generated PDF.
    """
    temp_dir = tempfile.mkdtemp()
    tex_path = os.path.join(temp_dir, "exam.tex")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_str)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=temp_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        pdf_path = os.path.join(temp_dir, "exam.pdf")
        if output_filename:
            final_dir = os.path.join(settings.MEDIA_ROOT, "exams")
            os.makedirs(final_dir, exist_ok=True)
            final_path = os.path.join(final_dir, output_filename)
            os.rename(pdf_path, final_path)
            return final_path

        return pdf_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError("LaTeX compilation failed. Ensure pdflatex is installed.") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during PDF compilation: {e}")


def render_exam_to_pdf(exam: Exam, include_answers=False, randomize=False, filename=None) -> str:
    """
    Renders an exam into PDF format.
    :param include_answers: Whether to include answers (True for teachers).
    :param randomize: Whether to shuffle questions.
    :param filename: Optional filename (slugified if not provided).
    """
    latex_code = generate_latex_exam(exam, include_answers=include_answers, randomize=randomize)
    filename = filename or f"{slugify(exam.name)}_{exam.id}.pdf"
    return compile_latex_to_pdf(latex_code, output_filename=filename)


def render_marking_scheme(exam: Exam) -> str:
    """
    Render a LaTeX version of the marking scheme for an exam.
    Returns a LaTeX string that can be compiled or stored.
    """
    context = {
        "exam": exam,
        "subjects": []
    }

    for subject in exam.subjects.all():
        questions = Question.objects.filter(
            assessment__title__icontains=exam.name,
            subject=subject.subject
        )
        data = []
        for q in questions:
            data.append({
                "text": q.text,
                "marks": q.marks,
                "guide": getattr(q.marking_scheme, 'guide', 'No guide available'),
                "rubrics": q.rubrics.all()
            })

        context["subjects"].append({
            "subject": subject.subject,
            "questions": data
        })

    try:
        return render_to_string("exams/templates/marking_scheme.tex", context)
    except Exception as e:
        raise RuntimeError(f"Failed to render marking scheme: {e}")
