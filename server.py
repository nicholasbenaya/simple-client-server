import socket
import threading
import sys

def dapatkan_ip_lokal():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

print("=== PENGATURAN SERVER ===")
print("1. Mode Simulasi Lokal (Hanya untuk 1 komputer)")
print("2. Mode Jaringan Ril (Buka untuk jaringan Wi-Fi/LAN)")
pilihan_jaringan = input("Pilih mode jaringan (1 atau 2): ").strip()

port_input = input("Masukkan Port Server (misal: 5000, 5001, dst): ").strip()
PORT = int(port_input) if port_input.isdigit() else 5000

print("\n=== PENGATURAN KEAMANAN ===")
print("1. PUBLIC (Klien bisa langsung bergabung)")
print("2. PRIVATE (Admin harus memberikan izin)")
pilihan_keamanan = input("Pilih keamanan (1 atau 2): ").strip()
is_private = (pilihan_keamanan == '2')

if pilihan_jaringan == '1':
    HOST = '127.0.0.1'
    ip_tampil = HOST
else:
    HOST = '0.0.0.0' 
    ip_tampil = dapatkan_ip_lokal()

print("\n" + "="*50)
print(f"[*] SERVER AKTIF DI: {ip_tampil}:{PORT}")
print(f"[*] MODE KEAMANAN: {'PRIVATE (Butuh Izin)' if is_private else 'PUBLIC (Terbuka)'}")
print("="*50)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server_socket.bind((HOST, PORT))
server_socket.settimeout(1.0) 

# --- PERUBAHAN PENTING ---
clients = {}              # Sekarang berupa Dictionary -> {address: username}
pending_clients = {}      # Dictionary -> {id: (address, username)}
next_pending_id = 1
server_berjalan = True 

def cek_status_pending(address):
    for addr, uname in pending_clients.values():
        if addr == address:
            return True
    return False

def jalankan_server():
    global clients, pending_clients, next_pending_id
    while server_berjalan: 
        try:
            message_bytes, client_address = server_socket.recvfrom(1024)
            pesan_teks = message_bytes.decode('utf-8')
            
            # 1. JIKA KLIEN SUDAH TERDAFTAR (Ini adalah pesan obrolan)
            if client_address in clients:
                pengirim = clients[client_address]
                pesan_lengkap = f"[{pengirim}]: {pesan_teks}"
                
                # Monitoring Traffic
                klien_lain = len(clients) - 1
                if klien_lain > 0:
                    print(f"\n[Traffic] Pesan dari {pengirim} diteruskan ke {klien_lain} klien.")
                    print("Admin> ", end="", flush=True)
                
                # Broadcast ke semua kecuali pengirim
                for addr in clients:
                    if addr != client_address:
                        server_socket.sendto(pesan_lengkap.encode('utf-8'), addr)
            
            # 2. JIKA KLIEN BARU PERTAMA KALI KONEK (Pesan ini adalah Username mereka)
            elif not cek_status_pending(client_address):
                username_baru = pesan_teks # Pesan pertama selalu dianggap sebagai Username
                
                if is_private:
                    pending_clients[next_pending_id] = (client_address, username_baru)
                    pesan_tunggu = "[SERVER] Anda berada di ruang tunggu. Menunggu izin Admin..."
                    server_socket.sendto(pesan_tunggu.encode('utf-8'), client_address)
                    
                    print(f"\n[!] ADMISSION: Klien '{username_baru}' (ID {next_pending_id}) ingin bergabung!")
                    print(f"[!] Ketik 'izin {next_pending_id}' atau 'tolak {next_pending_id}'")
                    print("Admin> ", end="", flush=True)
                    next_pending_id += 1
                else:
                    clients[client_address] = username_baru
                    print(f"\n[+] Klien baru bergabung: {username_baru} ({client_address})")
                    print("Admin> ", end="", flush=True)
                    
                    # Beritahu semua orang bahwa ada yang baru bergabung
                    pengumuman = f"[SERVER] {username_baru} telah bergabung ke dalam obrolan!"
                    for addr in clients:
                        if addr != client_address:
                            server_socket.sendto(pengumuman.encode('utf-8'), addr)
                    
        except socket.timeout:
            continue 
        except Exception as e:
            pass

thread_server = threading.Thread(target=jalankan_server)
thread_server.daemon = True
thread_server.start()

print("\n=== PANEL ADMIN ===")
print("- 'status' : Lihat klien aktif & mengantre")
print("- 'izin <ID>' : Terima klien (Khusus Private)")
print("- 'tolak <ID>': Tolak klien (Khusus Private)")
print("- 'stop'   : Matikan server\n")

while True:
    perintah = input("Admin> ").strip().lower()
    
    if perintah == 'stop':
        print("[*] Mematikan server...")
        server_berjalan = False   
        server_socket.close()     
        sys.exit(0)
        
    elif perintah == 'status':
        print("\n--- STATUS SERVER ---")
        print(f"Klien Aktif ({len(clients)}):")
        for addr, uname in clients.items():
            print(f" - {uname} ({addr})")
        print(f"Klien Menunggu ({len(pending_clients)}):")
        for id_tunggu, data in pending_clients.items():
            print(f" - ID {id_tunggu} : {data[1]} ({data[0]})")
        print("---------------------\n")
        
    elif perintah.startswith('izin '):
        try:
            id_target = int(perintah.split(' ')[1])
            if id_target in pending_clients:
                addr, uname = pending_clients.pop(id_target)
                clients[addr] = uname # Masukkan ke daftar resmi
                server_socket.sendto(f"[SERVER] [DISETUJUI] Selamat datang, {uname}!".encode('utf-8'), addr)
                print(f"[*] Klien '{uname}' diizinkan masuk.")
                
                # Umumkan ke klien lain
                for client_addr in clients:
                    if client_addr != addr:
                        server_socket.sendto(f"[SERVER] {uname} telah bergabung ke dalam obrolan!".encode('utf-8'), client_addr)
            else:
                print("[!] ID tidak ditemukan di ruang tunggu.")
        except:
            print("[!] Format salah. Gunakan: izin <angka>")
            
    elif perintah.startswith('tolak '):
        try:
            id_target = int(perintah.split(' ')[1])
            if id_target in pending_clients:
                addr, uname = pending_clients.pop(id_target)
                server_socket.sendto("[SERVER] [DITOLAK] Maaf, koneksi Anda ditolak oleh Admin.".encode('utf-8'), addr)
                print(f"[*] Klien '{uname}' telah ditolak.")
            else:
                print("[!] ID tidak ditemukan di ruang tunggu.")
        except:
            print("[!] Format salah. Gunakan: tolak <angka>")