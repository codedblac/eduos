# medical/ai_engine.py

from collections import Counter
from django.db.models import Count
from students.models import Student
from .models import SickBayVisit, MedicineInventory

def get_most_affected_classes(limit=5):
    """
    Returns top N most affected classes by number of medical visits.
    """
    visits = SickBayVisit.objects.values(
        'student__class_level__name',
        'student__stream__name'
    ).annotate(total=Count('id')).order_by('-total')[:limit]

    return [
        {
            "class_level": v['student__class_level__name'],
            "stream": v['student__stream__name'],
            "visits": v['total']
        }
        for v in visits
    ]


def get_common_symptoms(limit=10):
    """
    Returns top N most frequent symptoms recorded.
    """
    all_symptoms = SickBayVisit.objects.values_list('symptoms', flat=True)
    symptom_counter = Counter()

    for entry in all_symptoms:
        if entry:
            for symptom in entry.split(','):
                symptom_counter[symptom.strip().lower()] += 1

    return symptom_counter.most_common(limit)


def get_top_medicines_used(limit=10):
    """
    Returns top N most frequently used medicines.
    """
    usage = MedicineInventory.objects.values('name').annotate(total_used=Count('id')).order_by('-total_used')[:limit]
    return [
        {"medicine": item['name'], "used_count": item['total_used']}
        for item in usage
    ]
