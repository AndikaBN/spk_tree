#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smk_rekomendasi.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from rekomendasi.models import UserProfile, Student, Prediction

print("=== DEBUGGING DATA ===")

# Check Users
print("\n1. USERS:")
users = User.objects.all()
for user in users:
    print(f"   - {user.username} (superuser: {user.is_superuser})")
    if hasattr(user, 'profile'):
        print(f"     Profile: role={user.profile.role}, nis={user.profile.nis}")
    else:
        print(f"     Profile: TIDAK ADA")

# Check Students
print("\n2. STUDENTS:")
students = Student.objects.all()
for student in students:
    print(f"   - {student.name} (NIS: {student.nis})")

# Check Predictions
print("\n3. PREDICTIONS:")
predictions = Prediction.objects.all()
for pred in predictions:
    print(f"   - {pred.student.name} -> {pred.jurusan_prediksi} ({pred.probability:.2f}%)")

print(f"\nTOTAL: {users.count()} users, {students.count()} students, {predictions.count()} predictions")
