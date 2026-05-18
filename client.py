import socket
import threading
import os

# ==========================================
# MENU PENGATURAN AWAL KLIEN
# ==========================================
print("=== PENGATURAN KLIEN ===")
print("1. Hubungkan ke Server Lokal (Simulasi di 1 laptop yang sama)")
print("2. Hubungkan ke Server Teman (Jaringan Wi-Fi/LAN)")
pilihan = input("Pilih mode (1 atau 2): ").strip()

SERVER_PORT = 5000

if pilihan == '1':
    SERVER_HOST = '127.0.0.1'
    print("[*] Menyiapkan koneksi ke Server Lokal...")
else:
    # Meminta input IP secara dinamis dari pengguna
    SERVER_HOST = input("\nMasukkan IP Server yang diberikan oleh teman Anda: ").strip()
    print(f"[*] Menyiapkan koneksi ke {SERVER_HOST}...")

# ==========================================
# INTI PROGRAM KLIEN
# ==========================================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def receive_messages():
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(f"\r[Pesan Masuk]: {message.decode('utf-8')}\n> ", end="")
        except Exception as e:
            print(f"\n[!] Terjadi Error Penerimaan: {e}")
            print("[!] Menutup program klien secara otomatis...")
            os._exit(1) 

print("Menyambungkan ke server...")

try:
    sapaan_awal = "Halo, saya baru saja bergabung!"
    client_socket.sendto(sapaan_awal.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
except Exception as e:
    print(f"[!] Gagal terhubung: Pastikan IP benar dan Server sudah menyala. Error: {e}")
    os._exit(1)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

print("\n=== Selamat Datang di Chat UDP ===")
print("Ketik pesan Anda dan tekan Enter. Ketik 'keluar' untuk berhenti.\n")

while True:
    try:
        pesan_keluar = input("> ")
        
        if pesan_keluar.lower() == 'keluar':
            print("Meninggalkan obrolan...")
            client_socket.close()
            os._exit(0) 
            
        client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        
    except Exception as e:
        print(f"\n[!] Error Pengiriman: {e}")
        print("[!] Program dihentikan.")
        os._exit(1)