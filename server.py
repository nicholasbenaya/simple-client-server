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

print("=== PENGATURAN AWAL SERVER ===")
print("1. Mode Simulasi Lokal (Hanya untuk 1 komputer)")
print("2. Mode Jaringan Ril (Buka untuk jaringan Wi-Fi/LAN)")
pilihan_jaringan = input("Pilih mode jaringan (1 atau 2): ").strip()

port_input = input("Masukkan Port Server (misal: 5000): ").strip()
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

# --- NEW FEATURE: DNS REGISTRATION ---
print("\n=== PENGATURAN DNS (NAMA SERVER) ===")
pakai_dns = input("Daftarkan server ini ke DNS? (y/n): ").strip().lower()
if pakai_dns == 'y':
    dns_ip = input("Masukkan IP dari DNS Server: ").strip()
    nama_server = input("Masukkan Nama Unik untuk ruang obrolan ini (misal: Lobby-A): ").strip()
    
    try:
        # Send registration packet to DNS server on port 9000
        s_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_dns.settimeout(2.0)
        s_dns.sendto(f"REGISTER|{nama_server}|{ip_tampil}|{PORT}".encode('utf-8'), (dns_ip, 9000))
        resp, _ = s_dns.recvfrom(1024)
        if resp.decode('utf-8') == 'OK':
            print(f"[*] Berhasil terdaftar di DNS dengan nama: {nama_server}")
        s_dns.close()
    except Exception as e:
        print(f"[!] Gagal menghubungi DNS: {e}")
# --------------------------------------

print("\n" + "="*50)
print(f"[*] SERVER AKTIF DI: {ip_tampil}:{PORT}")
print(f"[*] MODE KEAMANAN: {'PRIVATE' if is_private else 'PUBLIC'}")
print("="*50)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
server_socket.bind((HOST, PORT))
server_socket.settimeout(1.0) 

clients = {}              
pending_clients = {}      
next_pending_id = 1
server_berjalan = True 

def cek_status_pending(address):
    for addr, uname in pending_clients.values():
        if addr == address: return True
    return False

def jalankan_server():
    global clients, pending_clients, next_pending_id, is_private
    while server_berjalan: 
        try:
            message_bytes, client_address = server_socket.recvfrom(1024)
            pesan_teks = message_bytes.decode('utf-8')
            
            if client_address in clients:
                pengirim = clients[client_address]
                if pesan_teks == "__KELUAR__":
                    print(f"\n[-] Klien terputus: {pengirim} ({client_address[0]}:{client_address[1]})")
                    print("Admin> ", end="", flush=True)
                    del clients[client_address]
                    for addr in clients:
                        server_socket.sendto(f"[SERVER] {pengirim} telah meninggalkan obrolan.".encode('utf-8'), addr)
                else:
                    pesan_lengkap = f"[{pengirim}]: {pesan_teks}"
                    for addr in clients:
                        if addr != client_address:
                            server_socket.sendto(pesan_lengkap.encode('utf-8'), addr)
            
            elif not cek_status_pending(client_address):
                username_baru = pesan_teks 
                if is_private:
                    pending_clients[next_pending_id] = (client_address, username_baru)
                    server_socket.sendto("[SERVER] Anda berada di ruang tunggu. Menunggu izin Admin...".encode('utf-8'), client_address)
                    print(f"\n[!] ADMISSION: Klien '{username_baru}' (ID {next_pending_id}) dari IP {client_address[0]}:{client_address[1]} ingin bergabung!")
                    print("Admin> ", end="", flush=True)
                    next_pending_id += 1
                else:
                    clients[client_address] = username_baru
                    print(f"\n[+] Klien bergabung: {username_baru} dari IP {client_address[0]}:{client_address[1]}")
                    print("Admin> ", end="", flush=True)
                    server_socket.sendto(f"[SERVER] Selamat datang di obrolan, {username_baru}!".encode('utf-8'), client_address)
                    for addr in clients:
                        if addr != client_address:
                            server_socket.sendto(f"[SERVER] {username_baru} bergabung!".encode('utf-8'), addr)
                    
        except socket.timeout: continue 
        except Exception: pass

thread_server = threading.Thread(target=jalankan_server)
thread_server.daemon = True
thread_server.start()

print("\n=== PANEL ADMIN ===")
print("- 'status' : Lihat klien aktif")
print("- 'izin <ID>' / 'tolak <ID>' : Kelola ruang tunggu")
print("- 'mode public' / 'mode private' : Ubah keamanan Server")
print("- 'stop'   : Matikan server\n")

while True:
    perintah = input("Admin> ").strip().lower()
    
    if perintah == 'stop':
        print("[*] Mematikan server. Memutuskan semua klien...")
        pesan_stop = "__SERVER_STOP__".encode('utf-8')
        for addr in list(clients.keys()): server_socket.sendto(pesan_stop, addr)
        for data in pending_clients.values(): server_socket.sendto(pesan_stop, data[0]) 
        server_berjalan = False   
        server_socket.close()     
        sys.exit(0)
    elif perintah == 'mode public':
        is_private = False
        print("[*] Server sekarang beroperasi di mode PUBLIC.")
    elif perintah == 'mode private':
        is_private = True
        print("[*] Server sekarang beroperasi di mode PRIVATE.")
    elif perintah == 'status':
        print(f"\n--- STATUS ({'PRIVATE' if is_private else 'PUBLIC'}) ---")
        print(f"Klien Aktif ({len(clients)}):")
        for addr, uname in clients.items(): print(f" - [{uname}] terhubung dari {addr[0]}:{addr[1]}")
        print(f"\nKlien Menunggu ({len(pending_clients)}):")
        for id_tunggu, data in pending_clients.items(): print(f" - ID {id_tunggu} : [{data[1]}] dari {data[0][0]}:{data[0][1]}")
        print("---------------------\n")
    elif perintah.startswith('izin '):
        try:
            id_target = int(perintah.split(' ')[1])
            if id_target in pending_clients:
                addr, uname = pending_clients.pop(id_target)
                clients[addr] = uname 
                server_socket.sendto(f"[SERVER] [DISETUJUI] Selamat datang, {uname}!".encode('utf-8'), addr)
                print(f"[*] Klien '{uname}' diizinkan masuk.")
                for client_addr in clients:
                    if client_addr != addr: server_socket.sendto(f"[SERVER] {uname} bergabung!".encode('utf-8'), client_addr)
            else: print("[!] ID tidak ditemukan.")
        except: pass
    elif perintah.startswith('tolak '):
        try:
            id_target = int(perintah.split(' ')[1])
            if id_target in pending_clients:
                addr, uname = pending_clients.pop(id_target)
                server_socket.sendto("[SERVER] [DITOLAK] Akses ditolak oleh Admin.".encode('utf-8'), addr)
                print(f"[*] Klien '{uname}' ditolak.")
        except: pass