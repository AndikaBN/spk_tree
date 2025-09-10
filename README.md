
# Sistem Rekomendasi Pemilihan Jurusan (Decision Tree • Django + MySQL)

Aplikasi web berbasis **Django** untuk membantu SMK YASPI merekomendasikan jurusan siswa
berdasarkan **Decision Tree** (ID3/CART) dengan fitur:
- Manajemen data siswa (MTK, B. Indonesia, B. Inggris, IPA, dan *minat*).
- Latih model dari dataset Excel (2 sheet: PERKANTORAN + AKUNTANSI).
- Prediksi jurusan per siswa + laporan hasil.
- UI sederhana (HTML + CSS) yang rapi.

> Alur dan modul mengikuti skripsi (login/admin/siswa, data siswa, perhitungan, hasil/laporan) namun metode disesuaikan ke **Decision Tree** sebagaimana diminta.

---

## 1) Prasyarat

- Python 3.10+
- MySQL 5.7+ / 8+ (opsional; default dev menggunakan SQLite)
- Pip + venv (virtualenv)
- (Windows) bisa pakai SQLite dulu; MySQL dapat dikonfigurasi belakangan.

## 2) Setup Cepat (Dev, SQLite)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Migrasi database
python manage.py migrate

# Buat superuser (login ke /admin atau /login)
python manage.py createsuperuser

# Jalankan server
python manage.py runserver
```

Buka: http://127.0.0.1:8000

## 3) Konfigurasi MySQL (Opsional/Produksi)

- Buat DB & (opsional) user:
```sql
SOURCE db_schema.sql;
```

- Set environment variables (salin `.env.sample` menjadi `.env` atau export manual):
```
DB_NAME=smk_rekomendasi
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
DJANGO_SECRET_KEY=ubah-ini
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Jalankan ulang migrasi:
```bash
python manage.py migrate
```

## 4) Struktur Dataset Excel

Gunakan **2 sheet pertama** di file Excel (contoh: `Sheet1` dan `Sheet2`). Pada data Anda, nama sheet mungkin `Sheet1` (PERKANTORAN) dan `Sheet4` (AKUNTANSI). Aplikasi akan membaca **dua sheet teratas**.

Format kolom per sheet (baris pertama bisa berisi judul kolom yang lebar):
```
NO | NAMA | NILAI MTK | NILAI B.INDO | NILAI B.ING | NILAI IPA | MINAT | JURUSAN
```
- Contoh nilai MINAT: `Administrasi` / `Berhitung` (opsional nilai lain).
- JURUSAN di-normalisasi menjadi: `AKUNTANSI` atau `PERKANTORAN`.

## 5) Melatih Model

**Via UI**
1. Login ke aplikasi (menu `Latih Model`).
2. Upload file Excel dataset (2 sheet).
3. Klik **Latih Sekarang**.
4. Model disimpan ke `media/decision_tree.pkl` dan siap dipakai.

**Via CLI (opsional)**
```bash
python manage.py load_dataset /path/ke/dataset.xlsx
# kemudian latih model via UI atau tambahkan fungsi CLI sendiri bila perlu
```

## 6) Memasukkan Data Siswa & Prediksi
1. Menu **Data Siswa** → **+ Tambah** untuk menambah siswa.
2. Klik tombol **Prediksi** pada baris siswa untuk menghasilkan rekomendasi jurusan.
3. Lihat semua hasil pada menu **Hasil** (bisa dicetak via Print as PDF).

## 7) Akurasi & Laporan
- Saat pelatihan, aplikasi menampilkan akurasi dan classification report (precision/recall/f1).
- Ke depannya Anda bisa menambah validasi silang atau threshold probabilitas.

## 8) Catatan Penting
- Model **Decision Tree** dipilih sesuai permintaan terbaru; skripsi yang lama memakai VIKOR. Alur UI tetap serupa: input data → proses → hasil.
- Paket DB untuk MySQL memakai **PyMySQL** (tanpa kompilasi). Jika ingin `mysqlclient`, pastikan *build tools* tersedia.

## 9) Troubleshooting
- **ImportError: MySQLdb** → pastikan `PyMySQL` terinstal (sudah ada di `requirements.txt`).
- **openpyxl error** → pastikan file Excel `.xlsx` valid dan tidak terbuka oleh aplikasi lain.
- **Akurasi rendah** → periksa kebersihan data (nilai numerik dan label jurusan konsisten), tambah fitur, atau atur `max_depth` di `rekomendasi/ml.py`.

---

Dibuat untuk: *SMK YASPI – Sistem rekomendasi pemilihan jurusan berbasis web, metode Decision Tree.*
