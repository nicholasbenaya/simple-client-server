import socket

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
registry = {}

print("="*50)
print(f"[*] DNS SERVER BERJALAN DI IP : {IP_PUBLIK}")
print(f"[*] PORT DNS                  : {PORT}")
print("="*50)
print("[*] Menunggu registrasi atau pencarian otomatis (Broadcast)...\n")

while True:
    try:
        data, addr = dns_socket.recvfrom(1024)
        message = data.decode('utf-8')
        parts = message.split('|')
        command = parts[0]

        # --- FITUR BARU: Menjawab teriakan Broadcast ---
        if command == 'DISCOVER_DNS':
            # Membalas ke pengirim agar mereka tahu IP kita
            dns_socket.sendto("I_AM_DNS".encode('utf-8'), addr)
            print(f"[>] Menjawab pencarian otomatis dari {addr[0]}")
        # -----------------------------------------------

        elif command == 'REGISTER':
            name, ip, port = parts[1], parts[2], int(parts[3])
            registry[name] = (ip, port)
            print(f"[+] Server Terdaftar: '{name}' di {ip}:{port}")
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

    except Exception as e:
        print(f"[!] Error DNS: {e}")