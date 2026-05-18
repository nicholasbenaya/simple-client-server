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

# --- Meminta Username dari Pengguna ---
while True:
    USERNAME = input("Masukkan Username Anda: ").strip()
    if USERNAME:
        break
    print("Username tidak boleh kosong!")

print(f"\n[*] Menyiapkan koneksi ke {SERVER_HOST}:{SERVER_PORT}...")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
            print(f"\n[!] Terputus dari server atau terjadi error: {e}")
            os._exit(1) 

print("Menyambungkan ke server...")

try:
    # --- Perubahan: Mengirim Username sebagai paket pertama ---
    client_socket.sendto(USERNAME.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
except Exception as e:
    print(f"[!] Gagal mengirim pesan awal. Error: {e}")
    os._exit(1)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

print("\n=== Selamat Datang di Chat UDP ===")
print("Ketik pesan Anda dan tekan Enter. Ketik 'keluar' untuk berhenti.\n")

while True:
    try:
        # Tampilan input disesuaikan dengan Username
        pesan_keluar = input(f"[{USERNAME}]> ")
        
        if pesan_keluar.lower() == 'keluar':
            print("Meninggalkan obrolan...")
            client_socket.close()
            os._exit(0) 
            
        if pesan_keluar.strip(): # Hanya kirim jika pesan tidak kosong
            client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        
    except KeyboardInterrupt:
        print("\nKeluar secara paksa...")
        os._exit(0)
    except Exception as e:
        print(f"\n[!] Error Pengiriman: {e}")
        os._exit(1)