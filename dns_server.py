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

HOST = '0.0.0.0'
PORT = 9000 
IP_PUBLIK = dapatkan_ip_lokal()

dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns_socket.bind((HOST, PORT))
dns_socket.settimeout(1.0) # Timeout agar thread tidak tersangkut selamanya
registry = {}
dns_berjalan = True

print("="*50)
print(f"[*] DNS SERVER BERJALAN DI IP : {IP_PUBLIK}")
print(f"[*] PORT DNS                  : {PORT}")
print("="*50)

# Memisahkan fungsi pendengar jaringan ke dalam Thread khusus
def jalankan_dns():
    global registry, dns_berjalan
    print("[*] Menunggu registrasi atau pencarian otomatis (Broadcast)...\n")
    while dns_berjalan:
        try:
            data, addr = dns_socket.recvfrom(1024)
            message = data.decode('utf-8')
            parts = message.split('|')
            command = parts[0]

            if command == 'DISCOVER_DNS':
                dns_socket.sendto("I_AM_DNS".encode('utf-8'), addr)
            elif command == 'REGISTER':
                name, ip, port = parts[1], parts[2], int(parts[3])
                registry[name] = (ip, port)
                dns_socket.sendto("OK".encode('utf-8'), addr)
            elif command == 'GET_LIST':
                if not registry:
                    dns_socket.sendto("EMPTY".encode('utf-8'), addr)
                else:
                    names = ",".join(registry.keys())
                    dns_socket.sendto(f"LIST|{names}".encode('utf-8'), addr)
            elif command == 'RESOLVE':
                name = parts[1]
                if name in registry:
                    ip, port = registry[name]
                    dns_socket.sendto(f"RES|{ip}|{port}".encode('utf-8'), addr)
                else:
                    dns_socket.sendto("NOT_FOUND".encode('utf-8'), addr)
        except socket.timeout:
            continue
        except Exception:
            pass

# Menjalankan Thread Jaringan
thread_dns = threading.Thread(target=jalankan_dns)
thread_dns.daemon = True
thread_dns.start()

# --- PANEL ADMIN DNS (Berjalan di Thread Utama) ---
print("=== PANEL ADMIN DNS ===")
print("- 'status' : Lihat server obrolan yang terdaftar")
print("- 'reset'  : Hapus semua daftar server")
print("- 'stop'   : Matikan DNS Server\n")

while True:
    try:
        perintah = input("DNS Admin> ").strip().lower()
        
        if perintah == 'stop':
            print("[*] Mematikan DNS Server...")
            dns_berjalan = False
            dns_socket.close()
            sys.exit(0)
            
        elif perintah == 'status':
            print(f"\n--- STATUS PENDAFTARAN DNS ---")
            if not registry:
                print("Belum ada server yang terdaftar.")
            else:
                for nama, (ip, port) in registry.items():
                    print(f" - [{nama}] beroperasi di {ip}:{port}")
            print("------------------------------\n")
            
        elif perintah == 'reset':
            registry.clear()
            print("[*] Memori DNS telah dibersihkan. Semua pendaftaran dihapus.")
            
    except KeyboardInterrupt:
        print("\n[*] Menutup DNS secara paksa...")
        dns_berjalan = False
        dns_socket.close()
        sys.exit(0)