import socket
import threading
import sys

def dapatkan_ip_lokal():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        return s.getsockname()[0]
    except: return "127.0.0.1"

def temukan_dns_server():
    print("\n[*] Mencari DNS Server di jaringan secara otomatis...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
    s.settimeout(2.0)
    try:
        s.sendto("DISCOVER_DNS".encode('utf-8'), ('255.255.255.255', 9000))
        data, addr = s.recvfrom(1024)
        if data.decode('utf-8') == "I_AM_DNS":
            print(f"[+] DNS Server ditemukan secara ajaib di IP: {addr[0]}!")
            s.close()
            return addr[0]
    except socket.timeout: print("[!] Gagal menemukan DNS secara otomatis.")
    s.close(); return None

print("=== PENGATURAN AWAL SERVER ===")
pilihan_jaringan = input("1. Lokal / 2. Jaringan Ril (Pilih 1/2): ").strip()
port_input = input("Masukkan Port Server (misal: 5000): ").strip()
PORT = int(port_input) if port_input.isdigit() else 5000

pilihan_keamanan = input("Keamanan: 1. PUBLIC / 2. PRIVATE (Pilih 1/2): ").strip()
is_private = (pilihan_keamanan == '2')

HOST = '127.0.0.1' if pilihan_jaringan == '1' else '0.0.0.0'
ip_tampil = HOST if pilihan_jaringan == '1' else dapatkan_ip_lokal()

# --- VARIABEL GLOBAL BARU UNTUK MENGINGAT DNS ---
dns_ip_aktif = None
nama_server_aktif = None
# ------------------------------------------------

print("\n=== PENGATURAN DNS (NAMA SERVER) ===")
pakai_dns = input("Daftarkan server ini ke DNS? (y/n): ").strip().lower()
if pakai_dns == 'y':
    dns_ip = temukan_dns_server() 
    if dns_ip: 
        nama_server = input("Masukkan Nama Unik ruang obrolan (misal: Lobby-A): ").strip()
        try:
            s_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s_dns.settimeout(2.0)
            s_dns.sendto(f"REGISTER|{nama_server}|{ip_tampil}|{PORT}".encode('utf-8'), (dns_ip, 9000))
            resp, _ = s_dns.recvfrom(1024)
            if resp.decode('utf-8') == 'OK':
                print(f"[*] Berhasil terdaftar di DNS dengan nama: {nama_server}")
                # Simpan informasi untuk proses Deregistrasi nanti
                dns_ip_aktif = dns_ip
                nama_server_aktif = nama_server
            s_dns.close()
        except Exception as e: print(f"[!] Gagal mendaftar ke DNS: {e}")
    else: print("[!] Melewati pendaftaran DNS.")

print("\n" + "="*50)
print(f"[*] SERVER AKTIF DI: {ip_tampil}:{PORT}")
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
                    for addr in clients: server_socket.sendto(f"[SERVER] {pengirim} meninggalkan obrolan.".encode('utf-8'), addr)
                else:
                    pesan_lengkap = f"[{pengirim}]: {pesan_teks}"
                    for addr in clients:
                        if addr != client_address: server_socket.sendto(pesan_lengkap.encode('utf-8'), addr)
            elif not cek_status_pending(client_address):
                username_baru = pesan_teks 
                if is_private:
                    pending_clients[next_pending_id] = (client_address, username_baru)
                    server_socket.sendto("[SERVER] Anda berada di ruang tunggu. Menunggu izin Admin...".encode('utf-8'), client_address)
                    print(f"\n[!] ADMISSION: '{username_baru}' dari IP {client_address[0]}:{client_address[1]} ingin bergabung!")
                    print("Admin> ", end="", flush=True)
                    next_pending_id += 1
                else:
                    clients[client_address] = username_baru
                    print(f"\n[+] Klien bergabung: {username_baru} dari IP {client_address[0]}:{client_address[1]}")
                    print("Admin> ", end="", flush=True)
                    server_socket.sendto(f"[SERVER] Selamat datang di obrolan, {username_baru}!".encode('utf-8'), client_address)
                    for addr in clients:
                        if addr != client_address: server_socket.sendto(f"[SERVER] {username_baru} bergabung!".encode('utf-8'), addr)
        except socket.timeout: continue 
        except Exception: pass

thread_server = threading.Thread(target=jalankan_server)
thread_server.daemon = True
thread_server.start()

print("\n=== PANEL ADMIN ===")
print("- 'status', 'izin <ID>', 'tolak <ID>', 'mode public', 'mode private', 'stop'")
while True:
    perintah = input("Admin> ").strip().lower()
    if perintah == 'stop':
        # --- FITUR BARU: PAMIT KE DNS SEBELUM MATI ---
        if dns_ip_aktif and nama_server_aktif:
            try:
                s_dns_pamit = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s_dns_pamit.sendto(f"DEREGISTER|{nama_server_aktif}".encode('utf-8'), (dns_ip_aktif, 9000))
                s_dns_pamit.close()
                print(f"[*] Berhasil menghapus pendaftaran '{nama_server_aktif}' dari DNS.")
            except: pass
        # ---------------------------------------------
        
        pesan_stop = "__SERVER_STOP__".encode('utf-8')
        for addr in list(clients.keys()): server_socket.sendto(pesan_stop, addr)
        for data in pending_clients.values(): server_socket.sendto(pesan_stop, data[0]) 
        server_berjalan = False   
        server_socket.close()     
        sys.exit(0)
    elif perintah == 'mode public': is_private = False; print("[*] Mode: PUBLIC")
    elif perintah == 'mode private': is_private = True; print("[*] Mode: PRIVATE")
    elif perintah == 'status':
        print(f"\n--- STATUS ---")
        for addr, uname in clients.items(): print(f" - [{uname}] dari {addr[0]}:{addr[1]}")
        for id_tunggu, data in pending_clients.items(): print(f" - ID {id_tunggu} : [{data[1]}] (Mengantre)")
        print("--------------\n")
    elif perintah.startswith('izin '):
        try:
            id = int(perintah.split(' ')[1])
            if id in pending_clients:
                addr, uname = pending_clients.pop(id)
                clients[addr] = uname 
                server_socket.sendto(f"[SERVER] [DISETUJUI] Selamat datang!".encode('utf-8'), addr)
                for c_addr in clients:
                    if c_addr != addr: server_socket.sendto(f"[SERVER] {uname} bergabung!".encode('utf-8'), c_addr)
        except: pass
    elif perintah.startswith('tolak '):
        try:
            id = int(perintah.split(' ')[1])
            if id in pending_clients:
                addr, uname = pending_clients.pop(id)
                server_socket.sendto("[SERVER] [DITOLAK] Akses ditolak.".encode('utf-8'), addr)
        except: pass