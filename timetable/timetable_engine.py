# timetable/ai_engine.py

from ortools.sat.python import cp_model
from .models import SubjectAssignment, TimetableEntry, Room
from classes.models import Stream
from datetime import timedelta
from django.db import transaction

# Constants
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
PERIODS_PER_DAY = 8  # Adjust as needed

def generate_ai_timetable():
    model = cp_model.CpModel()
    assignments = list(SubjectAssignment.objects.select_related('teacher', 'subject', 'stream'))
    rooms = list(Room.objects.all())
    
    if not rooms:
        raise Exception("No rooms available for timetable generation.")

    # Variables: (assignment_idx, day, period) -> assigned or not
    schedule_vars = {}
    for idx, assignment in enumerate(assignments):
        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                schedule_vars[(idx, d, p)] = model.NewBoolVar(f'sched_{idx}_{d}_{p}')

    # Constraint 1: Each assignment must be scheduled for its lessons_per_week
    for idx, assignment in enumerate(assignments):
        model.Add(sum(schedule_vars[(idx, d, p)] for d in range(len(DAYS)) for p in range(PERIODS_PER_DAY)) == assignment.lessons_per_week)

    # Constraint 2: No teacher overlaps
    for d in range(len(DAYS)):
        for p in range(PERIODS_PER_DAY):
            for teacher in set(a.teacher for a in assignments):
                model.Add(
                    sum(schedule_vars[(idx, d, p)]
                        for idx, a in enumerate(assignments) if a.teacher == teacher
                    ) <= 1
                )

    # Constraint 3: No stream overlaps
    for d in range(len(DAYS)):
        for p in range(PERIODS_PER_DAY):
            for stream in set(a.stream for a in assignments):
                model.Add(
                    sum(schedule_vars[(idx, d, p)]
                        for idx, a in enumerate(assignments) if a.stream == stream
                    ) <= 1
                )

    # Constraint 4: Limit room usage to available rooms
    for d in range(len(DAYS)):
        for p in range(PERIODS_PER_DAY):
            model.Add(
                sum(schedule_vars[(idx, d, p)] for idx in range(len(assignments))) <= len(rooms)
            )

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        raise Exception("No valid timetable could be generated. Please review constraints or input data.")

    # Clean previous entries
    TimetableEntry.objects.all().delete()

    # Write the result to TimetableEntry
    with transaction.atomic():
        used_rooms = rooms.copy()
        for idx, assignment in enumerate(assignments):
            for d in range(len(DAYS)):
                for p in range(PERIODS_PER_DAY):
                    if solver.Value(schedule_vars[(idx, d, p)]) == 1:
                        room = used_rooms.pop(0) if used_rooms else rooms[0]
                        TimetableEntry.objects.create(
                            teacher=assignment.teacher,
                            subject=assignment.subject,
                            stream=assignment.stream,
                            day_of_week=DAYS[d],
                            period=p + 1,
                            room=room
                        )
                        used_rooms.append(room)  # reuse room next time

