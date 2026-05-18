# Python UDP Chat Room

Sebuah aplikasi obrolan (chat) berbasis command-line menggunakan protokol UDP. Proyek ini mendemonstrasikan pemrograman jaringan (*socket programming*) dasar di Python dengan dukungan Multi-Server, Pemantauan Lalu Lintas (Traffic Monitoring), dan Sistem Keamanan (Public/Private).

## Fitur Utama
- **Arsitektur Client-Server:** Menggunakan protokol UDP yang ringan dan cepat.
- **Dukungan Lintas Platform:** Berjalan di Windows, Linux (termasuk WSL), dan macOS.
- **Username Identitas:** Setiap klien akan diminta memasukkan nama sebelum bergabung.
- **Keamanan (Public & Private Mode):**
  - *Public:* Klien bebas bergabung secara otomatis.
  - *Private:* Klien masuk ke 'Ruang Tunggu' dan harus diizinkan (Admission) oleh Admin Server.
- **Port Dinamis & Multiserver:** Memungkinkan satu komputer menjalankan beberapa server sekaligus pada Port yang berbeda.
- **Panel Admin:** Server dilengkapi antarmuka untuk memonitor klien aktif, klien menunggu, dan lalu lintas pesan.

## Persyaratan Sistem
- Python 3.x terinstal di komputer Anda.
- Tidak memerlukan pustaka (library) eksternal. Semua menggunakan bawaan Python (`socket`, `threading`, `os`, `sys`).

## Cara Menggunakan

### 1. Menjalankan Server
Buka terminal/command prompt, arahkan ke folder proyek, dan jalankan:
```bash
python3 server.py 
# (Atau gunakan `py server.py` jika menggunakan Windows Launcher)