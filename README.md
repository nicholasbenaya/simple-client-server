# 💬 Python UDP Chat Room (Advanced)

Sebuah aplikasi obrolan (*chat*) berbasis *command-line* (CLI) yang persisten dan tangguh, dibangun murni menggunakan protokol jaringan UDP di Python. Proyek ini mendemonstrasikan implementasi *socket programming*, manajemen status klien (*state management*), sistem *graceful shutdown*, konfigurasi jaringan *on-the-fly*, dan pemantauan lalu lintas.

---

## ✨ Fitur Utama

- **Arsitektur Cepat & Ringan (UDP):** Memanfaatkan protokol UDP (*User Datagram Protocol*) untuk pengiriman pesan instan dengan latensi minimal.
- **Siklus Hidup Klien yang Persisten:** Klien memiliki Menu Utama interaktif. Jika terputus dari server, klien tidak akan *crash*, melainkan kembali ke Menu Utama.
- **Graceful Shutdown:** Saat Server dimatikan, Server akan menyiarkan sinyal penutupan ke seluruh klien agar mereka terputus secara aman dan elegan.
- **Sistem Identitas & Hotkey:** - Pengguna diwajibkan mendaftarkan *username* sebelum masuk.
  - Menggunakan kombinasi tombol **`Ctrl + C`** untuk keluar dari ruang obrolan secara aman (kembali ke Menu Utama).
- **Port Dinamis & Multiserver:** Mendukung inisiasi banyak server secara simultan di dalam satu mesin fisik yang sama.
- **Keamanan Ruang Obrolan (On-the-Fly Config):**
  - 🌍 **Public Mode:** Pengguna dapat langsung terhubung.
  - 🔒 **Private Mode:** Pengguna ditahan di *Waiting Room* hingga mendapat persetujuan (*Admission*).
  - *Status keamanan dapat diubah oleh Admin kapan saja tanpa perlu me-restart Server.*
- **Cross-Platform:** Kompatibel penuh untuk Windows, macOS, maupun Linux (termasuk WSL).

---

## ⚙️ Persyaratan Sistem

Aplikasi ini tidak memerlukan instalasi *library* eksternal. Anda hanya membutuhkan:
- **Python 3.6+** terinstal di mesin Anda.

---

## 🚀 Panduan Penggunaan

### 1. Menjalankan Server
Buka terminal/Command Prompt, lalu jalankan:
```bash
# Pengguna Windows:
python server.py 

# Pengguna Linux / WSL / macOS:
python3 server.py
```
**Langkah Inisialisasi:**
1. Pilih **Mode Jaringan**: `1` untuk *Localhost* atau `2` untuk jaringan ril (LAN/Wi-Fi).
2. Masukkan **Port**: (misal: `5000`).
3. Pilih **Tingkat Keamanan**: `1` (*Public*) atau `2` (*Private*).

### 2. Menjalankan Klien
Buka terminal baru di komputer yang sama atau komputer lain di jaringan yang sama, lalu jalankan:
```bash
# Pengguna Windows:
python client.py

# Pengguna Linux / WSL / macOS:
python3 client.py
```
**Navigasi Menu:**
1. Anda akan disambut oleh **Menu Utama**. Pilih mode jaringan yang sesuai.
2. Masukkan **IP Address Server** dan **Port Server**.
3. Masukkan **Username** Anda.
4. Saat berada di dalam ruang obrolan, tekan **`Ctrl + C`** kapan saja untuk keluar dan kembali ke Menu Utama. Pilih opsi `3` di Menu Utama jika ingin menutup aplikasi sepenuhnya.

---

## 🛠️ Panel Perintah Admin (Server)

Ketikkan perintah berikut langsung di terminal Server untuk mengontrol ekosistem obrolan secara *real-time*:

| Perintah | Deskripsi Fungsi |
| :--- | :--- |
| `status` | Menampilkan daftar klien yang sedang *online* dan klien di *Waiting Room*. |
| `izin <ID>` | Memberikan akses masuk kepada klien di ruang tunggu (Khusus *Private*). |
| `tolak <ID>`| Menolak akses klien secara paksa dari ruang tunggu. |
| `mode public` | Mengubah keamanan server menjadi *Public* seketika. Klien baru langsung masuk. |
| `mode private`| Mengubah keamanan server menjadi *Private* seketika. Klien baru butuh izin. |
| `stop` | Mengirim sinyal pemutusan ke semua klien dan mematikan server dengan aman. |

---

## 🔍 Cara Membuktikan Protokol UDP

Anda dapat memverifikasi secara langsung melalui sistem operasi bahwa program ini benar-benar berjalan di jalur UDP (bukan TCP).
1. Pastikan program `server.py` sedang berjalan (misalnya pada port `5000`).
2. Buka terminal atau Command Prompt **baru**.
3. Jalankan perintah pelacak jaringan di bawah ini:

```bash
# Untuk pengguna Windows (Command Prompt / PowerShell):
netstat -an | findstr 5000

# Untuk pengguna Linux / macOS / WSL:
netstat -an | grep 5000
```
**Hasil yang Diharapkan:** Anda akan melihat baris output yang diawali dengan kata **`UDP`** (Contoh: `UDP 0.0.0.0:5000 *:*`). Ini membuktikan secara mutlak bahwa kurir data yang digunakan adalah *User Datagram Protocol*.

---

## 🐛 Troubleshooting (Pemecahan Masalah)

- **Klien tersangkut pada pesan "Menunggu konfirmasi" lalu terputus**
  Pastikan Anda telah memasukkan IP dan Port yang benar. Jika Anda menggunakan beda komputer, pastikan Anda mematikan (*Turn Off*) **Windows Defender Firewall** sementara di laptop Server, karena Windows secara *default* memblokir lalu lintas UDP yang masuk.
- **Klien mengirim pesan tapi tidak sampai (Miskomunikasi Subnet)**
  Jika Anda menggunakan Docker/VirtualBox, IP yang terdeteksi server mungkin adalah IP Virtual. Pastikan menggunakan IP asli Wi-Fi/LAN dengan mengecek `ipconfig` (Windows) atau `ifconfig` (Linux) secara manual.
- **Tidak dapat terhubung di Wi-Fi Kampus/Kafe (AP Isolation)**
  Banyak jaringan publik memblokir komunikasi *peer-to-peer* (AP Isolation) atau *port* non-standar. Solusi terbaik adalah menggunakan *Mobile Hotspot* (Tethering) dari ponsel untuk menguji koneksi antar dua laptop.
- **Error: Perintah tidak dikenali di Terminal (Windows)**
  Pastikan Python telah ditambahkan ke PATH *Environment Variables*. Atau, gunakan perintah `py` alih-alih `python`.