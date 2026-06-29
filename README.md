# HoaxCheck: Deploy Gratis di Vercel

Paket ini sudah disiapkan untuk Vercel Hobby. Frontend dan backend berada dalam satu domain:
- Frontend: `public/index.html`
- API FastAPI: `api/index.py`
- Endpoint: `/api/deteksi`

## Sebelum deploy

1. **Cabut API key lama di Groq sekarang juga.** Key lama pernah tersimpan langsung di kode asli.
2. Buat API key Groq baru.
3. Jangan masukkan key baru ke file `.py`, `.html`, atau GitHub.
4. Buat akun GitHub dan Vercel. Gunakan paket **Hobby**, bukan trial Pro.

## Cara deploy

1. Ekstrak ZIP ini.
2. Buat repository GitHub baru, misalnya `hoaxcheck`.
3. Unggah semua isi folder ini ke repository tersebut.
4. Buka Vercel, pilih **Add New > Project**, lalu import repository tadi.
5. Pada bagian **Environment Variables**, tambah:
   - Name: `GROQ_API_KEY`
   - Value: API key Groq baru
   - Environments: Production, Preview, Development
6. Klik **Deploy**.
7. Setelah selesai, buka URL yang diberikan Vercel dan uji aplikasi.

Tidak perlu mengisi Build Command atau Start Command.

## Batas gratis

- Vercel Hobby ditujukan untuk project pribadi atau akademik. Jika kuota habis, fitur terkait berhenti sementara, bukan otomatis menagih.
- API Groq juga memakai kuota gratis. Bila limit harian/menit tercapai, tombol analisis akan menampilkan error sampai limit tersedia lagi.
- Aplikasi ini cocok untuk tugas kuliah, demo, dan portofolio. Jangan gunakan sebagai layanan publik bertrafik tinggi tanpa rate limiting dan pengelolaan biaya.

## Uji lokal opsional

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.index:app --reload
```

Untuk menjalankan frontend lokal, buka `public/index.html` melalui Live Server atau server statis apa pun. API lokal akan tetap perlu disesuaikan jika tidak memakai Vercel.
