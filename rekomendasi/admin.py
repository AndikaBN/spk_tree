
from django.contrib import admin
from .models import Student, Prediction, TrainingRecord

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "nis", "jurusan")
    search_fields = ("name", "nis", "jurusan")

@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("name", "nilai_mtk", "nilai_bindo", "nilai_bing", "nilai_ipa", "minat", "jurusan")
    list_filter = ("jurusan", "minat")

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "jurusan_prediksi", "probability", "created_at")
    list_filter = ("jurusan_prediksi",)
