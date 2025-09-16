from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rekomendasi.models import UserProfile

class Command(BaseCommand):
    help = 'Create demo users with different roles'

    def handle(self, *args, **options):
        # Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@smkyaspi.edu',
                'first_name': 'Administrator',
                'last_name': 'System',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.get_or_create(
                user=admin_user, 
                defaults={'role': 'admin', 'phone': '081234567890'}
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin123'))
        else:
            # Ensure profile exists
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user, 
                defaults={'role': 'admin', 'phone': '081234567890'}
            )
            self.stdout.write(self.style.WARNING(f'Admin user already exists'))

        # Create Kepala Sekolah User
        kepsek_user, created = User.objects.get_or_create(
            username='kepsek',
            defaults={
                'email': 'kepsek@smkyaspi.edu',
                'first_name': 'Kepala',
                'last_name': 'Sekolah',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            kepsek_user.set_password('kepsek123')
            kepsek_user.save()
            UserProfile.objects.get_or_create(
                user=kepsek_user, 
                defaults={'role': 'kepala_sekolah', 'phone': '081234567891'}
            )
            self.stdout.write(self.style.SUCCESS(f'Created kepala sekolah user: kepsek/kepsek123'))
        else:
            # Ensure profile exists
            profile, created = UserProfile.objects.get_or_create(
                user=kepsek_user, 
                defaults={'role': 'kepala_sekolah', 'phone': '081234567891'}
            )
            self.stdout.write(self.style.WARNING(f'Kepala sekolah user already exists'))

        # Create Siswa User  
        siswa_user, created = User.objects.get_or_create(
            username='siswa',
            defaults={
                'email': 'siswa@smkyaspi.edu',
                'first_name': 'Siswa',
                'last_name': 'Demo',
                'is_staff': False,
                'is_superuser': False
            }
        )
        if created:
            siswa_user.set_password('siswa123')
            siswa_user.save()
            UserProfile.objects.get_or_create(
                user=siswa_user, 
                defaults={'role': 'siswa', 'nis': 'SIS12345678', 'phone': '081234567892'}
            )
            self.stdout.write(self.style.SUCCESS(f'Created siswa user: siswa/siswa123'))
        else:
            # Ensure profile exists
            profile, created = UserProfile.objects.get_or_create(
                user=siswa_user, 
                defaults={'role': 'siswa', 'nis': 'SIS12345678', 'phone': '081234567892'}
            )
            self.stdout.write(self.style.WARNING(f'Siswa user already exists'))

        self.stdout.write(self.style.SUCCESS('\n=== DEMO USERS CREATED ==='))
        self.stdout.write(self.style.SUCCESS('Admin: admin/admin123'))
        self.stdout.write(self.style.SUCCESS('Kepala Sekolah: kepsek/kepsek123'))
        self.stdout.write(self.style.SUCCESS('Siswa: siswa/siswa123'))
        self.stdout.write(self.style.SUCCESS('========================\n'))
    