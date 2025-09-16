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
from rekomendasi.decorators import get_user_role

print("=== DEBUG USER KEPSEK ===")

try:
    # Cari user kepsek
    kepsek_user = User.objects.get(username='kepsek')
    print(f"✅ User 'kepsek' ditemukan:")
    print(f"   - Username: {kepsek_user.username}")
    print(f"   - Email: {kepsek_user.email}")
    print(f"   - Is_superuser: {kepsek_user.is_superuser}")
    
    # Cek profile
    if hasattr(kepsek_user, 'profile'):
        print(f"   - Profile exists: YES")
        print(f"   - Role: {kepsek_user.profile.role}")
        print(f"   - NIS: {kepsek_user.profile.nis}")
        print(f"   - Phone: {kepsek_user.profile.phone}")
        
        # Test get_user_role function
        role = get_user_role(kepsek_user)
        print(f"   - get_user_role() returns: {role}")
        
        # Test dashboard logic
        if role == 'siswa':
            print("   - 🚨 PROBLEM: Role adalah 'siswa' - akan menampilkan dashboard siswa!")
        elif role == 'kepala_sekolah':
            print("   - ✅ OK: Role adalah 'kepala_sekolah' - akan menampilkan dashboard kepala sekolah")
        else:
            print(f"   - ⚠️  UNEXPECTED: Role adalah '{role}'")
            
    else:
        print(f"   - Profile exists: NO")
        print("   - 🚨 PROBLEM: User tidak punya profile!")
        
except User.DoesNotExist:
    print("❌ User 'kepsek' tidak ditemukan!")
    print("\nUsers yang ada:")
    for user in User.objects.all():
        print(f"   - {user.username}")

print("\n=== SEMUA USER PROFILES ===")
for user in User.objects.all():
    if hasattr(user, 'profile'):
        print(f"   - {user.username}: role='{user.profile.role}'")
    else:
        print(f"   - {user.username}: NO PROFILE")