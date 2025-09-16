#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smk_rekomendasi.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from rekomendasi.models import UserProfile

print("=== FIXING USER PROFILES ===")

# Create missing profiles
users_without_profile = User.objects.filter(profile__isnull=True)
for user in users_without_profile:
    if user.username == 'kepala-sekolahh@':
        role = 'kepala_sekolah'
    elif user.is_superuser:
        role = 'admin'
    else:
        role = 'siswa'
    
    UserProfile.objects.create(user=user, role=role)
    print(f"Created profile for {user.username} with role {role}")

# Update existing profiles that need role correction
users_with_wrong_role = User.objects.filter(username__in=['kepsek'])
for user in users_with_wrong_role:
    if hasattr(user, 'profile'):
        user.profile.role = 'kepala_sekolah'
        user.profile.save()
        print(f"Updated {user.username} role to kepala_sekolah")

print("\n=== CURRENT USER PROFILES ===")
users = User.objects.all()
for user in users:
    if hasattr(user, 'profile'):
        print(f"   - {user.username}: role={user.profile.role}")
    else:
        print(f"   - {user.username}: NO PROFILE")
