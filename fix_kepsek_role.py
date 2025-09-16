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

print("=== FIXING KEPSEK ROLE ===")

try:
    # Cari user kepsek
    kepsek_user = User.objects.get(username='kepsek')
    
    # Cek/buat profile
    if hasattr(kepsek_user, 'profile'):
        current_role = kepsek_user.profile.role
        print(f"Current role for 'kepsek': {current_role}")
        
        if current_role != 'kepala_sekolah':
            kepsek_user.profile.role = 'kepala_sekolah'
            kepsek_user.profile.save()
            print(f"✅ Updated role from '{current_role}' to 'kepala_sekolah'")
        else:
            print("✅ Role sudah benar: kepala_sekolah")
    else:
        # Buat profile baru
        UserProfile.objects.create(
            user=kepsek_user, 
            role='kepala_sekolah'
        )
        print("✅ Created new profile with role 'kepala_sekolah'")
        
except User.DoesNotExist:
    print("❌ User 'kepsek' tidak ditemukan!")
    print("Membuat user kepsek baru...")
    
    kepsek_user = User.objects.create_user(
        username='kepsek',
        email='kepsek@smkyaspi.edu',
        password='kepsek123',
        first_name='Kepala',
        last_name='Sekolah'
    )
    
    UserProfile.objects.create(
        user=kepsek_user,
        role='kepala_sekolah'
    )
    print("✅ Created new user 'kepsek' with role 'kepala_sekolah'")

print("\n=== FINAL CHECK ===")
kepsek_user = User.objects.get(username='kepsek')
print(f"User 'kepsek' role: {kepsek_user.profile.role}")