import socket
import threading
import sys

def dapatkan_ip_lokal():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        return s.getsockname()[0]
    except: return "127.0.0.1"

# --- FUNGSI AUTO-DISCOVERY UNTUK KLIEN ---
def temukan_dns_server():
    print("\n[*] Mencari DNS Server di jaringan secara otomatis...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(2.0)
    try:
        s.sendto("DISCOVER_DNS".encode('utf-8'), ('255.255.255.255', 9000))
        data, addr = s.recvfrom(1024)
        if data.decode('utf-8') == "I_AM_DNS":
            print(f"[+] DNS Server otomatis ditemukan di IP: {addr[0]}!")
            s.close()
            return addr[0]
    except socket.timeout:
        print("[!] DNS Server tidak ditemukan.")
    s.close()
    return None
# ----------------------------------------

def jalankan_menu_utama():
    while True:
        print("\n" + "="*40)
        print("           MENU UTAMA KLIEN           ")
        print("="*40)
        print("1. Hubungkan Manual (Ketik IP & Port)")
        print("2. Cari Ruang Obrolan Tersedia (Otomatis via DNS)")
        print("3. Keluar dari Program")
        
        try:
            pilihan = input("Pilih menu (1/2/3): ").strip()
            
            if pilihan == '3':
                sys.exit(0) 
                
            elif pilihan == '1':
                host = input("Masukkan IP Server: ").strip()
                port = int(input("Masukkan Port Server: ").strip())
                mulai_sesi_obrolan(host, port) 
                
            elif pilihan == '2':
                # Memanggil DNS secara otomatis, Anda tidak perlu mengetik IP lagi!
                dns_ip = temukan_dns_server()
                
                if not dns_ip:
                    print("\n[!] Kembali ke menu utama karena DNS tidak ditemukan.")
                    continue
                
                try:
                    s_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s_dns.settimeout(3.0)
                    
                    s_dns.sendto("GET_LIST".encode('utf-8'), (dns_ip, 9000))
                    data, _ = s_dns.recvfrom(1024)
                    respon = data.decode('utf-8')
                    
                    if respon == "EMPTY":
                        print("\n[!] Belum ada ruang obrolan yang terdaftar di DNS saat ini.")
                        continue
                        
                    elif respon.startswith("LIST|"):
                        names = respon.split('|')[1].split(',')
                        print("\n--- DAFTAR RUANG OBROLAN TERSEDIA ---")
                        for n in names:
                            print(f"  > {n}")
                        print("-------------------------------------")
                        
                        target_name = input("\nKetik nama ruang obrolan yang ingin dimasuki: ").strip()
                        
                        s_dns.sendto(f"RESOLVE|{target_name}".encode('utf-8'), (dns_ip, 9000))
                        data2, _ = s_dns.recvfrom(1024)
                        respon2 = data2.decode('utf-8')
                        
                        if respon2.startswith("RES|"):
                            parts = respon2.split('|')
                            resolved_ip = parts[1]
                            resolved_port = int(parts[2])
                            print(f"[*] Menghubungkan ke {target_name}...")
                            
                            mulai_sesi_obrolan(resolved_ip, resolved_port)
                        else:
                            print(f"\n[!] Nama '{target_name}' tidak ditemukan di DNS.")
                except Exception as e:
                    print(f"\n[!] Terjadi kesalahan komunikasi DNS: {e}")
            else:
                print("[!] Pilihan tidak valid.")
        except KeyboardInterrupt:
            sys.exit(0)

def mulai_sesi_obrolan(SERVER_HOST, SERVER_PORT):
    while True:
        USERNAME = input("Masukkan Username Anda: ").strip()
        if USERNAME: break

    print(f"\n[*] Menyiapkan koneksi ke ruang obrolan...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try: client_socket.bind((dapatkan_ip_lokal(), 0)) 
    except: pass

    koneksi_aktif = True 
    print("Menyambungkan ke server... (Menunggu konfirmasi)")
    try:
        client_socket.sendto(USERNAME.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        client_socket.settimeout(5.0) 
        message, _ = client_socket.recvfrom(1024)
        pesan_awal = message.decode('utf-8')
        print(f"\n{pesan_awal}")
        if "[DITOLAK]" in pesan_awal:
            print("\n[!] Kembali ke menu utama...")
            client_socket.close()
            return 
        client_socket.settimeout(1.0) 
    except socket.timeout:
        print("\n[!] Gagal terhubung: Server tidak merespons.")
        client_socket.close()
        return
    except Exception as e:
        client_socket.close()
        return

    def receive_messages():
        nonlocal koneksi_aktif
        while koneksi_aktif:
            try:
                message, _ = client_socket.recvfrom(1024)
                pesan_masuk = message.decode('utf-8')
                if pesan_masuk == "__SERVER_STOP__":
                    print("\n\n[!] KONEKSI TERPUTUS: Server telah dimatikan.")
                    print("[!] Tekan ENTER untuk kembali.")
                    koneksi_aktif = False
                    break
                if "[DITOLAK]" in pesan_masuk:
                    print(f"\n\n{pesan_masuk}")
                    koneksi_aktif = False
                    break
                print(f"\r{pesan_masuk}\n[{USERNAME}]> ", end="", flush=True)
            except socket.timeout: continue 
            except Exception:
                if koneksi_aktif: print("\n[!] Terputus dari server.")
                koneksi_aktif = False
                break

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    print("\n" + "="*30)
    print(" SELAMAT DATANG DI RUANG OBROLAN ")
    print(" [INFO] Tekan 'Ctrl + C' untuk keluar.")
    print("="*30 + "\n")

    while koneksi_aktif:
        try:
            pesan_keluar = input(f"[{USERNAME}]> ")
            if not koneksi_aktif: break 
            if pesan_keluar.strip(): client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        except KeyboardInterrupt:
            print("\n\n[*] Meninggalkan ruang obrolan...")
            try: client_socket.sendto("__KELUAR__".encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            except: pass
            koneksi_aktif = False
            break 
    client_socket.close()

if __name__ == "__main__":
    jalankan_menu_utama()