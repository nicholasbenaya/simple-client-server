import socket

HOST = '0.0.0.0'
PORT = 9000 # Using port 9000 for our custom DNS

dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns_socket.bind((HOST, PORT))

# Dictionary to store registered servers: { "ServerName": ("IP", Port) }
registry = {}

print(f"[*] DNS Server is actively running on Port {PORT}...")
print("[*] Waiting for server registrations or client queries...\n")

while True:
    try:
        data, addr = dns_socket.recvfrom(1024)
        message = data.decode('utf-8')
        parts = message.split('|')
        command = parts[0]

        if command == 'REGISTER':
            # Format: REGISTER|Name|IP|Port
            name = parts[1]
            ip = parts[2]
            port = int(parts[3])
            registry[name] = (ip, port)
            print(f"[+] Registered New Server: '{name}' at {ip}:{port}")
            dns_socket.sendto("OK".encode('utf-8'), addr)

        elif command == 'GET_LIST':
            # Format: GET_LIST
            if not registry:
                dns_socket.sendto("EMPTY".encode('utf-8'), addr)
            else:
                names = ",".join(registry.keys())
                dns_socket.sendto(f"LIST|{names}".encode('utf-8'), addr)

        elif command == 'RESOLVE':
            # Format: RESOLVE|Name
            name = parts[1]
            if name in registry:
                ip, port = registry[name]
                dns_socket.sendto(f"RES|{ip}|{port}".encode('utf-8'), addr)
            else:
                dns_socket.sendto("NOT_FOUND".encode('utf-8'), addr)

    except Exception as e:
        print(f"[!] DNS Error: {e}")