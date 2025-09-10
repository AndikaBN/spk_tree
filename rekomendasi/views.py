
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

@login_required
def decision_tree_view(request, student_id):
    """View untuk menampilkan visualisasi pohon keputusan"""
    student = get_object_or_404(Student, id=student_id)
    
    # Check if model exists
    if not Path(MODEL_PATH).exists():
        messages.error(request, "Model belum dilatih! Silakan latih model terlebih dahulu.")
        return redirect('train_model')
    
    # Handle save prediction
    if request.method == 'POST' and request.POST.get('save_prediction'):
        try:
            # Get prediction
            prediction, probability, _ = predict_single(
                student.nilai_mtk, student.nilai_bindo, 
                student.nilai_bing, student.nilai_ipa, student.minat
            )
            
            # Save prediction
            Prediction.objects.create(
                student=student,
                jurusan_prediksi=prediction,
                probability=probability
            )
            
            messages.success(request, f"Hasil prediksi untuk {student.name} berhasil disimpan!")
            return redirect('results')
            
        except Exception as e:
            messages.error(request, f"Gagal menyimpan prediksi: {str(e)}")
    
    try:
        # Get prediction result
        prediction, probability, probabilities = predict_single(
            student.nilai_mtk, student.nilai_bindo, 
            student.nilai_bing, student.nilai_ipa, student.minat
        )
        
        # Calculate average score
        avg_score = (student.nilai_mtk + student.nilai_bindo + 
                    student.nilai_bing + student.nilai_ipa) / 4
        
        # Generate decision steps based on rules
        decision_steps = generate_decision_steps(student, prediction, probability)
        
        # Generate explanation text
        explanation_text = generate_explanation(student, prediction, avg_score)
        
        # Get feature importance (mock data for now)
        feature_importance = get_feature_importance(student, prediction)
        
        context = {
            'student': student,
            'prediction_result': prediction,
            'confidence': probability * 100,
            'avg_score': avg_score,
            'decision_steps': decision_steps,
            'explanation_text': explanation_text,
            'feature_importance': feature_importance,
        }
        
        return render(request, 'decision_tree.html', context)
        
    except Exception as e:
        messages.error(request, f"Gagal memuat pohon keputusan: {str(e)}")
        return redirect('predict_for_student', student_id=student_id)

def generate_decision_steps(student, prediction, probability):
    """Generate decision steps for visualization"""
    steps = []
    avg_score = (student.nilai_mtk + student.nilai_bindo + 
                student.nilai_bing + student.nilai_ipa) / 4
    
    # Step 1: Average Score Analysis
    if avg_score >= 80:
        score_tendency = "Tinggi"
        score_confidence = 85
    elif avg_score >= 70:
        score_tendency = "Sedang-Tinggi"  
        score_confidence = 75
    else:
        score_tendency = "Sedang"
        score_confidence = 65
        
    steps.append({
        'feature': '📊 Analisis Nilai Rata-rata',
        'condition': f'Rata-rata nilai = {avg_score:.1f} → Kategori {score_tendency}',
        'result': f'Indikasi awal: {prediction}',
        'confidence': score_confidence
    })
    
    # Step 2: Subject Strength Analysis
    subject_scores = {
        'Matematika': student.nilai_mtk,
        'B.Indonesia': student.nilai_bindo,
        'B.Inggris': student.nilai_bing,
        'IPA': student.nilai_ipa
    }
    
    strongest_subject = max(subject_scores, key=subject_scores.get)
    strongest_score = subject_scores[strongest_subject]
    
    if strongest_subject == 'Matematika' and strongest_score >= 80:
        subject_tendency = "AKUNTANSI"
        subject_confidence = 80
    elif strongest_subject in ['B.Indonesia', 'B.Inggris'] and strongest_score >= 75:
        subject_tendency = "PERKANTORAN"
        subject_confidence = 75
    else:
        subject_tendency = prediction  # Follow overall prediction
        subject_confidence = 70
        
    steps.append({
        'feature': '🎯 Analisis Kekuatan Mata Pelajaran',
        'condition': f'Nilai tertinggi: {strongest_subject} ({strongest_score}) → Mendukung {subject_tendency}',
        'result': f'Kecenderungan: {subject_tendency}',
        'confidence': subject_confidence
    })
    
    # Step 3: Interest Analysis
    interest_mapping = {
        'Berhitung': 'AKUNTANSI',
        'Analisis Data': 'AKUNTANSI', 
        'Keuangan': 'AKUNTANSI',
        'Administrasi': 'PERKANTORAN',
        'Komunikasi': 'PERKANTORAN',
        'Korespodensi': 'PERKANTORAN'
    }
    
    interest_prediction = interest_mapping.get(student.minat, prediction)
    interest_confidence = 90 if interest_prediction == prediction else 60
    
    steps.append({
        'feature': '💡 Analisis Minat Siswa',
        'condition': f'Minat "{student.minat}" → Cocok untuk {interest_prediction}',
        'result': f'Rekomendasi: {interest_prediction}',
        'confidence': interest_confidence
    })
    
    return steps

def generate_explanation(student, prediction, avg_score):
    """Generate explanation text for the prediction"""
    
    explanations = {
        'AKUNTANSI': f"""
        Berdasarkan analisis data siswa {student.name}, sistem merekomendasikan jurusan AKUNTANSI karena:
        
        • Rata-rata nilai akademik ({avg_score:.1f}) menunjukkan kemampuan yang baik dalam bidang eksak
        • Nilai Matematika ({student.nilai_mtk}) mendukung kemampuan berhitung yang diperlukan
        • Minat "{student.minat}" selaras dengan karakteristik jurusan Akuntansi
        • Kombinasi nilai IPA ({student.nilai_ipa}) dan kemampuan analisis mendukung keputusan ini
        
        Jurusan Akuntansi akan memberikan peluang karir di bidang keuangan, perpajakan, dan manajemen bisnis.
        """,
        
        'PERKANTORAN': f"""
        Berdasarkan analisis data siswa {student.name}, sistem merekomendasikan jurusan PERKANTORAN karena:
        
        • Rata-rata nilai akademik ({avg_score:.1f}) menunjukkan kemampuan yang seimbang
        • Nilai Bahasa Indonesia ({student.nilai_bindo}) dan Bahasa Inggris ({student.nilai_bing}) mendukung kemampuan komunikasi
        • Minat "{student.minat}" selaras dengan karakteristik jurusan Perkantoran
        • Profil akademik menunjukkan kesesuaian dengan kebutuhan administrasi dan manajemen kantor
        
        Jurusan Perkantoran akan memberikan peluang karir di bidang administrasi, sekretaris, dan manajemen kantor.
        """
    }
    
    return explanations.get(prediction, "Analisis tidak tersedia untuk prediksi ini.")

def get_feature_importance(student, prediction):
    """Get feature importance for visualization (mock implementation)"""
    
    # Calculate relative importance based on student data
    scores = [student.nilai_mtk, student.nilai_bindo, student.nilai_bing, student.nilai_ipa]
    avg = sum(scores) / len(scores)
    
    importance_data = [
        {
            'name': 'Nilai Matematika',
            'importance': abs(student.nilai_mtk - avg) / 100 + 0.3,
            'importance_percent': min(90, (abs(student.nilai_mtk - avg) / 100 + 0.3) * 100)
        },
        {
            'name': 'Minat Siswa', 
            'importance': 0.85,
            'importance_percent': 85
        },
        {
            'name': 'Nilai B.Indonesia',
            'importance': abs(student.nilai_bindo - avg) / 100 + 0.25,
            'importance_percent': min(80, (abs(student.nilai_bindo - avg) / 100 + 0.25) * 100)
        },
        {
            'name': 'Nilai B.Inggris',
            'importance': abs(student.nilai_bing - avg) / 100 + 0.2,
            'importance_percent': min(75, (abs(student.nilai_bing - avg) / 100 + 0.2) * 100)
        },
        {
            'name': 'Nilai IPA',
            'importance': abs(student.nilai_ipa - avg) / 100 + 0.15,
            'importance_percent': min(70, (abs(student.nilai_ipa - avg) / 100 + 0.15) * 100)
        }
    ]
    
    # Sort by importance
    importance_data.sort(key=lambda x: x['importance'], reverse=True)
    
    return importance_data
