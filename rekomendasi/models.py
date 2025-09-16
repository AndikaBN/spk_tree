
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

MINAT_CHOICES = [
    ("Administrasi", "Administrasi"),
    ("Komunikasi", "Komunikasi"),
    ("Korespodensi", "Korespodensi"),
    ("Berhitung", "Berhitung"),
    ("Analisis Data", "Analisis Data"),
    ("Keuangan", "Keuangan"),
]

JURUSAN_CHOICES = [
    ("AKUNTANSI", "Akuntansi & Keuangan Lembaga"),
    ("PERKANTORAN", "Manajemen Perkantoran & Layanan Bisnis"),
]

class Student(models.Model):
    name = models.CharField(max_length=150)
    nis = models.CharField(max_length=50, unique=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    nilai_mtk = models.FloatField(default=0)
    nilai_bindo = models.FloatField(default=0)
    nilai_bing = models.FloatField(default=0)
    nilai_ipa = models.FloatField(default=0)
    minat = models.CharField(max_length=40, choices=MINAT_CHOICES, default="Administrasi")

    jurusan = models.CharField(max_length=20, choices=JURUSAN_CHOICES, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.nis:
            # Auto generate NIS
            import uuid
            self.nis = f"SIS{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.nis})"

class TrainingRecord(models.Model):
    # Dataset baris untuk melatih model
    name = models.CharField(max_length=150)
    nilai_mtk = models.FloatField()
    nilai_bindo = models.FloatField()
    nilai_bing = models.FloatField()
    nilai_ipa = models.FloatField()
    minat = models.CharField(max_length=40)
    jurusan = models.CharField(max_length=20, choices=JURUSAN_CHOICES)

    def __str__(self):
        return f"{self.name} -> {self.jurusan}"

class Prediction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    jurusan_prediksi = models.CharField(max_length=20, choices=JURUSAN_CHOICES)
    probability = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} => {self.jurusan_prediksi} ({self.probability:.2f})"

ROLE_CHOICES = [
    ('admin', 'Administrator'),
    ('siswa', 'Siswa'),
    ('kepala_sekolah', 'Kepala Sekolah'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='siswa')
    nis = models.CharField(max_length=50, blank=True, null=True, help_text="Khusus untuk siswa")
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_siswa(self):
        return self.role == 'siswa'
    
    @property
    def is_kepala_sekolah(self):
        return self.role == 'kepala_sekolah'

# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance, 
            role='admin' if instance.is_superuser else 'siswa'
        )

@receiver(post_save, sender=User) 
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
