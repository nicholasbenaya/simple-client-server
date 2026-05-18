import socket
import threading
import sys

# Fungsi bantuan untuk mendeteksi IP Wi-Fi/LAN laptop secara otomatis
def dapatkan_ip_lokal():
    try:
        # Trik: Berpura-pura konek ke internet untuk melihat IP lokal mana yang terpakai
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Jika tidak ada jaringan, kembalikan ke localhost
        return "127.0.0.1"

# ==========================================
# MENU PENGATURAN AWAL SERVER
# ==========================================
print("=== PENGATURAN SERVER ===")
print("1. Mode Simulasi Lokal (Hanya untuk 1 laptop yang sama)")
print("2. Mode Jaringan Ril (Laptop teman bisa bergabung)")
pilihan = input("Pilih mode (1 atau 2): ").strip()

PORT = 5000

if pilihan == '1':
    HOST = '127.0.0.1'
    print(f"\n[*] Menjalankan Server di Mode Lokal...")
else:
    HOST = '0.0.0.0' # 0.0.0.0 artinya mendengarkan dari semua sumber jaringan masuk
    ip_publik = dapatkan_ip_lokal()
    print(f"\n[*] Menjalankan Server di Mode Jaringan Ril...")
    print("=" * 50)
    print(f" INFO PENTING: Beritahu teman Anda untuk memasukkan IP ini:")
    print(f" --->  {ip_publik}  <---")
    print("=" * 50)

# ==========================================
# INTI PROGRAM SERVER
# ==========================================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(1.0) 

clients = set()
server_berjalan = True 

def jalankan_server():
    global clients
    while server_berjalan: 
        try:
            message, client_address = server_socket.recvfrom(1024)
            
            if client_address not in clients:
                clients.add(client_address)
                print(f"\n[+] Klien baru bergabung dari: {client_address}")
                print("Admin> ", end="", flush=True) 

            for client in clients:
                if client != client_address:
                    server_socket.sendto(message, client)
                    
        except socket.timeout:
            continue 
        except Exception as e:
            if server_berjalan: 
                print(f"\n[!] Terjadi kesalahan: {e}")

thread_server = threading.Thread(target=jalankan_server)
thread_server.daemon = True
thread_server.start()

print("\n=== Panel Admin Server Aktif ===")
print("- Ketik 'stop' untuk mematikan server.")
print("- Ketik 'restart' untuk mereset daftar klien.\n")

while True:
    perintah = input("Admin> ").strip().lower()
    
    if perintah == 'stop':
        print("[*] Mematikan server. Menghentikan semua koneksi...")
        server_berjalan = False   
        server_socket.close()     
        sys.exit()                
        
    elif perintah == 'restart':
        clients.clear()           
        print("[*] Server di-restart! Memori daftar klien telah dibersihkan.")
        
    elif perintah != '':
        print("[!] Perintah tidak dikenali. Gunakan 'stop' atau 'restart'.")