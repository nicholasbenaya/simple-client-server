# 💬 Python UDP Chat Room

Sebuah aplikasi obrolan (*chat*) berbasis *command-line* (CLI) yang ringan dan cepat, dibangun murni menggunakan protokol jaringan UDP di Python. Proyek ini mendemonstrasikan implementasi *socket programming*, penanganan multithreading, sistem keamanan akses (*Admission*), dan pemantauan lalu lintas paket.

---

## ✨ Fitur Utama

- **Arsitektur Cepat & Ringan:** Menggunakan UDP (*User Datagram Protocol*) untuk latensi pengiriman pesan yang sangat rendah.
- **Sistem Identitas Klien:** Setiap pengguna diwajibkan mendaftarkan *username* sebelum bergabung, membuat obrolan lebih terstruktur.
- **Port Dinamis & Multiserver:** Mendukung inisiasi banyak server (simultan) di dalam satu mesin fisik yang sama melalui penugasan port secara dinamis.
- **Keamanan Ruang Obrolan:**
  - 🌍 **Public Mode:** Pengguna dapat langsung terhubung ke dalam ruang obrolan.
  - 🔒 **Private Mode:** Pengguna akan ditahan di *Waiting Room* hingga Admin memberikan izin (*Admission*).
- **Admin Dashboard:** Server dilengkapi panel pemantauan (*monitoring*) untuk melacak status pengguna aktif, pengguna yang mengantre, dan log lalu lintas penerusan paket.
- **Cross-Platform:** Kompatibel untuk dijalankan di lingkungan Windows, macOS, maupun distribusi Linux (termasuk WSL).

---

## ⚙️ Persyaratan Sistem

Aplikasi ini dibangun menggunakan modul bawaan standar, sehingga **tidak memerlukan instalasi *library* eksternal**. Anda hanya membutuhkan:
- **Python 3.6** atau versi yang lebih baru terinstal di mesin Anda.

---

## 🚀 Panduan Penggunaan

### 1. Menjalankan Server
Server berfungsi sebagai pusat *relay* pesan antar klien.

Buka terminal/Command Prompt, lalu jalankan perintah berikut:
```bash
# Untuk pengguna Windows:
python server.py 
# (Gunakan `py server.py` jika perintah python tidak dikenali)

# Untuk pengguna Linux / WSL / macOS:
python3 server.py
```

**Langkah Konfigurasi Server:**
1. Pilih **Mode Jaringan**: Pilih `1` untuk simulasi *Localhost* atau `2` untuk jaringan ril (LAN/Wi-Fi).
2. Masukkan **Port**: Tentukan port yang tersedia (misal: `5000`, `8080`, dll).
3. Pilih **Tingkat Keamanan**: Pilih `1` untuk *Public* atau `2` untuk *Private*.
> **Catatan:** Jika Anda memilih mode jaringan ril (2), catat **IP Address Publik** yang ditampilkan di layar untuk dibagikan kepada klien.

### 2. Menjalankan Klien
Klien adalah pengguna akhir yang akan saling berkirim pesan. Anda dapat menjalankan banyak sesi klien di berbagai komputer yang terhubung dalam satu jaringan.

Buka terminal baru, lalu jalankan:
```bash
# Pengguna Windows:
python client.py

# Pengguna Linux / WSL / macOS:
python3 client.py
```

**Langkah Konfigurasi Klien:**
1. Pilih **Mode Jaringan**: Sesuaikan dengan mode yang dipilih Server.
2. Masukkan **IP Address Server**: (Berdasarkan IP yang diberikan oleh Admin Server).
3. Masukkan **Port Server**.
4. Masukkan **Username** Anda sebagai identitas obrolan.

---

## 🛠️ Panel Perintah Admin (Server)

Saat server sedang berjalan, Admin dapat mengetikkan perintah berikut langsung di terminal server untuk mengontrol jaringan:

| Perintah | Deskripsi Fungsi |
| :--- | :--- |
| `status` | Menampilkan daftar klien yang sedang *online* dan detail klien yang berada di *Waiting Room*. |
| `izin <ID>` | Memberikan akses masuk kepada klien di ruang tunggu (Khusus Mode *Private*). Contoh: `izin 1` |
| `tolak <ID>`| Menolak permintaan akses klien dan memutus koneksinya secara paksa. Contoh: `tolak 1` |
| `stop` | Menghentikan paksa (*terminate*) semua operasi server dan menutup *socket*. |

---

## 🐛 Troubleshooting (Pemecahan Masalah)

- **Error: Perintah tidak dikenali di Terminal (Windows)**
  Pastikan Anda telah menambahkan Python ke PATH *Environment Variables* saat instalasi. Sebagai alternatif, gunakan perintah `py` alih-alih `python`.
- **Error: Program berjalan lancar, namun klien tidak bisa saling terhubung di beda komputer**
  Ini kemungkinan besar diblokir oleh OS. Pastikan Anda mengizinkan (*Allow Access*) program Python melalui **Windows Defender Firewall** atau matikan *firewall* untuk jaringan privat/lokal secara sementara.
- **Tidak dapat menjalankan program di WSL (Windows Subsystem for Linux) / Ubuntu**
  Lingkungan Linux secara ketat membedakan versi Python. Pastikan Anda mengeksekusi *script* secara eksplisit menggunakan perintah `python3`, bukan `python`.