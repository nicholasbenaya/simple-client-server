import socket
import threading
import os

print("=== PENGATURAN KLIEN ===")
print("1. Hubungkan ke Server Lokal (1 komputer)")
print("2. Hubungkan ke Server Teman (Jaringan Wi-Fi/LAN)")
pilihan = input("Pilih mode (1 atau 2): ").strip()

if pilihan == '1':
    SERVER_HOST = '127.0.0.1'
else:
    SERVER_HOST = input("Masukkan IP Server tujuan: ").strip()

port_input = input("Masukkan Port Server (misal 5000): ").strip()
SERVER_PORT = int(port_input) if port_input.isdigit() else 5000

# Meminta Username
while True:
    USERNAME = input("Masukkan Username Anda: ").strip()
    if USERNAME:
        break
    print("Username tidak boleh kosong!")

print(f"\n[*] Menyiapkan koneksi ke {SERVER_HOST}:{SERVER_PORT}...")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- PERUBAHAN UTAMA: VALIDASI KONEKSI (HANDSHAKE) ---
print("Menyambungkan ke server... (Menunggu konfirmasi)")

try:
    # 1. Kirim pesan perkenalan (Username)
    client_socket.sendto(USERNAME.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
    
    # 2. Beri waktu tunggu maksimal 5 detik untuk balasan server
    client_socket.settimeout(5.0) 
    
    # 3. Tunggu pesan konfirmasi dari server (bisa pesan ruang tunggu atau disetujui)
    message, _ = client_socket.recvfrom(1024)
    pesan_awal = message.decode('utf-8')
    print(f"\n{pesan_awal}")
    
    if "[DITOLAK]" in pesan_awal:
        os._exit(0)
        
    # 4. Jika berhasil mendapat balasan, matikan batas waktu agar bisa chatting normal
    client_socket.settimeout(None) 
    
except socket.timeout:
    # Jika 5 detik berlalu tanpa balasan, berarti Firewall memblokir atau IP salah
    print("\n[!] Gagal terhubung: Server tidak merespons.")
    print("[!] Pastikan IP benar dan Firewall di laptop Server telah dimatikan/diizinkan.")
    os._exit(1)
except Exception as e:
    print(f"\n[!] Error jaringan: {e}")
    os._exit(1)
# -----------------------------------------------------

# Fungsi pendengar pesan lanjutan (setelah koneksi awal berhasil)
def receive_messages():
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            pesan_masuk = message.decode('utf-8')
            
            print(f"\r{pesan_masuk}\n[{USERNAME}]> ", end="")
            
            if "[DITOLAK]" in pesan_masuk:
                print("\n[!] Menutup program karena ditolak server.")
                os._exit(0)
                
        except Exception as e:
            print(f"\n[!] Terputus dari server atau terjadi error.")
            os._exit(1) 

# Jalankan thread pendengar
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

print("\n=== Selamat Datang di Chat UDP ===")
print("Ketik pesan Anda dan tekan Enter. Ketik 'keluar' untuk berhenti.\n")

while True:
    try:
        pesan_keluar = input(f"[{USERNAME}]> ")
        
        if pesan_keluar.lower() == 'keluar':
            print("Meninggalkan obrolan...")
            client_socket.close()
            os._exit(0) 
            
        if pesan_keluar.strip(): 
            client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            
    except Exception as e:
        print(f"\n[!] Error Pengiriman: {e}")
        os._exit(1)