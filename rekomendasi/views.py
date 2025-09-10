
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from .models import Student, Prediction, TrainingRecord
from .forms import StudentForm, UploadDatasetForm
from pathlib import Path
import pandas as pd
from .ml import train_from_excel, load_or_train_default, predict_single, MODEL_PATH, _normalize_dataframe, get_calculation_details

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {
        "student_count": Student.objects.count(),
        "prediction_count": Prediction.objects.count(),
        "model_ready": Path(MODEL_PATH).exists(),
    })

@login_required
def students_list(request):
    qs = Student.objects.all().order_by("name")
    return render(request, "students_list.html", {"students": qs})

@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, "Data siswa disimpan.")
            return redirect("students_list")
    else:
        form = StudentForm()
    return render(request, "student_form.html", {"form": form, "title": "Tambah Siswa"})

@login_required
def student_edit(request, pk):
    obj = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Data siswa diperbarui.")
            return redirect("students_list")
    else:
        form = StudentForm(instance=obj)
    return render(request, "student_form.html", {"form": form, "title": "Ubah Siswa"})

@login_required
def student_delete(request, pk):
    obj = get_object_or_404(Student, pk=pk)
    obj.delete()
    messages.info(request, "Data siswa dihapus.")
    return redirect("students_list")

@login_required
def train_model(request):
    context = {}
    if request.method == "POST":
        form = UploadDatasetForm(request.POST, request.FILES)
        if form.is_valid():
            excel = form.cleaned_data["excel_file"]
            # Save to media/tmp and train
            media_dir = Path(settings.MEDIA_ROOT)
            media_dir.mkdir(parents=True, exist_ok=True)
            path = media_dir / "dataset.xlsx"
            with open(path, "wb") as out:
                for chunk in excel.chunks():
                    out.write(chunk)
            acc, report, model_path = train_from_excel(path)
            messages.success(request, f"Model dilatih. Akurasi: {acc:.2%}")
            context["report"] = report
            context["model_path"] = str(model_path)
        else:
            messages.error(request, "Form tidak valid.")
    else:
        form = UploadDatasetForm()
    context["form"] = form
    context["model_ready"] = Path(MODEL_PATH).exists()
    return render(request, "train.html", context)

@login_required
def results(request):
    qs = Prediction.objects.select_related("student").order_by("-created_at")
    return render(request, "results.html", {"predictions": qs})

@login_required
def calculation_details(request, student_id=None):
    """Halaman untuk melihat detail perhitungan entropy dan Decision Tree"""
    context = {
        "model_ready": Path(MODEL_PATH).exists(),
    }
    
    calculation_result = None
    student = None
    
    # Jika ada student_id, ambil data siswa dan lakukan perhitungan otomatis
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        if not Path(MODEL_PATH).exists():
            messages.error(request, "Model belum dilatih. Silakan latih model terlebih dahulu.")
            return redirect("train_model")
        
        try:
            calculation_result = get_calculation_details(
                student.nilai_mtk, student.nilai_bindo, student.nilai_bing, 
                student.nilai_ipa, student.minat
            )
            
            if calculation_result and 'error' not in calculation_result:
                messages.success(request, f"Perhitungan berhasil untuk {student.name}!")
            else:
                messages.error(request, f"Error dalam perhitungan: {calculation_result.get('error', 'Unknown error')}")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
    
    if request.method == "POST":
        if 'save_prediction' in request.POST and calculation_result and student:
            # Simpan hasil prediksi
            try:
                prediction = calculation_result['prediction']
                probability = calculation_result['probability']
                
                Prediction.objects.create(
                    student=student, 
                    jurusan_prediksi=prediction, 
                    probability=probability
                )
                messages.success(request, f"Hasil prediksi untuk {student.name} telah disimpan!")
                return redirect("results")
            except Exception as e:
                messages.error(request, f"Gagal menyimpan prediksi: {str(e)}")
        else:
            # Manual calculation (existing code)
            try:
                nilai_mtk = float(request.POST.get('nilai_mtk', 0))
                nilai_bindo = float(request.POST.get('nilai_bindo', 0))
                nilai_bing = float(request.POST.get('nilai_bing', 0))
                nilai_ipa = float(request.POST.get('nilai_ipa', 0))
                minat = request.POST.get('minat', 'Administrasi')
                
                if all(0 <= nilai <= 100 for nilai in [nilai_mtk, nilai_bindo, nilai_bing, nilai_ipa]):
                    calculation_result = get_calculation_details(nilai_mtk, nilai_bindo, nilai_bing, nilai_ipa, minat)
                    
                    if calculation_result and 'error' not in calculation_result:
                        messages.success(request, f"Perhitungan berhasil! Prediksi: {calculation_result['prediction']}")
                    else:
                        messages.error(request, f"Error dalam perhitungan: {calculation_result.get('error', 'Unknown error')}")
                else:
                    messages.error(request, "Nilai harus antara 0-100")
            except ValueError:
                messages.error(request, "Input tidak valid. Pastikan semua nilai adalah angka.")
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {str(e)}")
    
    context['calculation_result'] = calculation_result
    context['student'] = student
    context['minat_choices'] = [
        'Administrasi', 'Komunikasi', 'Korespodensi', 'Berhitung', 'Analisis Data', 'Keuangan'
    ]
    
    return render(request, "calculation_details.html", context)

def custom_logout(request):
    """Custom logout view dengan pesan konfirmasi - handle GET dan POST"""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f"Anda telah berhasil logout. Sampai jumpa, {username}!")
    return redirect('login')
