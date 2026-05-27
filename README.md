# 💬 Python UDP Chat Room with Custom DNS

Sebuah ekosistem aplikasi obrolan (*chat*) CLI tingkat lanjut, dibangun murni menggunakan protokol jaringan UDP di Python. Proyek ini bukan hanya sekadar obrolan, melainkan mendemonstrasikan ekosistem *Service Discovery* otomatis tanpa konfigurasi rumit (*Zero-Config*).

---

## ✨ Fitur Utama

- **Arsitektur Cepat & Ringan:** Menggunakan *User Datagram Protocol* (UDP) untuk pengiriman instan.
- **Sistem DNS Khusus (Service Discovery):** Dilengkapi `dns_server.py` yang bertindak sebagai buku telepon. 
  - Klien dan Server akan menemukan IP DNS secara otomatis menggunakan teknik **UDP Broadcasting**.
  - Pengguna hanya perlu mengingat "Nama Ruang Obrolan" (misal: *Lobby-A*), bukan IP dan Port.
- **Siklus Hidup Klien & Hotkey:** Klien tidak mati saat *disconnect*, melainkan kembali ke Menu Utama. Keluar ruang obrolan menggunakan kombinasi tombol `Ctrl + C`.
- **Keamanan Dinamis (*On-the-Fly*):** Admin dapat mengubah keamanan (*Public* atau *Private*) seketika saat server sedang berjalan.
- **Manajemen Server (Graceful Shutdown):** Saat Server utama atau DNS dimatikan, mereka akan memutus memori klien dengan aman tanpa menyebabkan *crash*.

---

## 🚀 Panduan Eksekusi Program (Berurutan)

Anda kini memiliki 3 komponen. Jalankan secara berurutan di terminal yang berbeda.

### Langkah 1: Jalankan DNS Server
Program ini adalah fondasi yang menghubungkan nama obrolan dengan IP asli.
```bash
python dns_server.py
```
> **Catatan:** DNS akan berjalan di latar belakang dan memiliki panel khusus untuk mereset daftar atau mematikan DNS.

### Langkah 2: Jalankan Chat Server
Buka terminal baru, lalu inisialisasi ruang obrolan Anda.
```bash
python server.py
```
**Langkah Konfigurasi:**
1. Atur mode (Lokal/Ril) dan keamanan (Public/Private).
2. Saat ditanya tentang **DNS**, pilih `y` (ya).
3. Server akan mendeteksi DNS secara gaib. Masukkan **Nama Ruang Obrolan** Anda (misal: `Ruang-Game`).

### Langkah 3: Jalankan Chat Client
Buka terminal baru di laptop Anda atau laptop teman (dalam 1 jaringan Wi-Fi/Hotspot).
```bash
python client.py
```
**Langkah Konfigurasi:**
1. Pilih opsi **2** (*Cari Ruang Obrolan via DNS*).
2. Klien akan mendeteksi DNS, mengambil daftar ruang obrolan yang aktif, dan menampilkannya di layar.
3. Ketikkan nama ruang obrolan (misal: `Ruang-Game`) untuk masuk.

---

## 🛠️ Panel Perintah Admin

### DNS Admin (`dns_server.py`)
| Perintah | Deskripsi |
| :--- | :--- |
| `status` | Menampilkan semua ruang obrolan dan IP yang terdaftar saat ini. |
| `reset` | Menghapus semua nama yang terdaftar dari memori tanpa mematikan program. |
| `stop` | Mematikan sistem DNS. |

### Chat Admin (`server.py`)
| Perintah | Deskripsi |
| :--- | :--- |
| `status` | Melihat IP Klien yang *online* maupun Klien di *Waiting Room*. |
| `izin <ID>` / `tolak <ID>` | Memberikan akses atau menolak akses klien (Mode Private). |
| `mode public` / `mode private` | Mengubah sistem keamanan secara *live*. |
| `stop` | Mengirim sinyal pemutusan ke semua Klien dan mematikan server. |

---

## 🐛 Troubleshooting & Tips Jaringan

1. **Broadcast UDP Gagal / DNS Tidak Ditemukan:** Fitur penemuan otomatis menggunakan alamat *Broadcast* (`255.255.255.255`). Jika DNS tidak terdeteksi:
   - Pastikan Anda menggunakan **Mobile Hotspot** pribadi (hindari Wi-Fi kampus karena memiliki fitur isolasi AP).
   - Pastikan **Windows Defender Firewall** dimatikan pada Profil **Private** maupun **Public**.
2. **Klien / Server Bingung Memilih IP (Masalah WSL/Docker):**
   Program sudah dilengkapi fitur penguncian (*bind*) ke kartu Wi-Fi asli. Namun jika masih gagal, matikan sementara *Virtual Adapter* (seperti `vEthernet` atau `VirtualBox`) di menu `ncpa.cpl` pada OS Windows.
3. **Pembuktian UDP Protocol:**
   Gunakan perintah `netstat -an | findstr <PORT>` (Windows) atau `netstat -an | grep <PORT>` (Linux). Anda akan melihat tulisan `UDP` berdampingan dengan *port* yang Anda pakai.