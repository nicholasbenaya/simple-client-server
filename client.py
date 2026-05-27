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

def jalankan_menu_utama():
    while True:
        print("\n" + "="*40)
        print("           MENU UTAMA KLIEN           ")
        print("="*40)
        print("1. Hubungkan Manual (Masukkan IP & Port)")
        print("2. Cari Ruang Obrolan via DNS (Nama Server)")
        print("3. Keluar dari Program")
        
        try:
            pilihan = input("Pilih menu (1/2/3): ").strip()
            
            if pilihan == '3':
                print("[*] Terima kasih telah menggunakan aplikasi ini. Sampai jumpa!")
                sys.exit(0) 
                
            elif pilihan == '1':
                # Manual connection
                host = input("Masukkan IP Server: ").strip()
                port = int(input("Masukkan Port Server: ").strip())
                mulai_sesi_obrolan(host, port) 
                
            elif pilihan == '2':
                # --- NEW FEATURE: DNS RESOLUTION ---
                dns_ip = input("Masukkan IP dari DNS Server: ").strip()
                
                try:
                    s_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s_dns.settimeout(3.0)
                    
                    # 1. Ask for the list of names
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
                        
                        # 2. Ask user to pick a name to resolve
                        target_name = input("Ketik nama ruang obrolan yang ingin dimasuki: ").strip()
                        
                        s_dns.sendto(f"RESOLVE|{target_name}".encode('utf-8'), (dns_ip, 9000))
                        data2, _ = s_dns.recvfrom(1024)
                        respon2 = data2.decode('utf-8')
                        
                        if respon2.startswith("RES|"):
                            parts = respon2.split('|')
                            resolved_ip = parts[1]
                            resolved_port = int(parts[2])
                            print(f"[*] Berhasil menemukan {target_name} di {resolved_ip}:{resolved_port}")
                            
                            # Start chat using resolved info!
                            mulai_sesi_obrolan(resolved_ip, resolved_port)
                        else:
                            print(f"\n[!] Nama '{target_name}' tidak ditemukan di DNS.")
                except socket.timeout:
                    print("\n[!] DNS Server tidak merespons. Pastikan IP DNS benar dan server menyala.")
                except Exception as e:
                    print(f"\n[!] Terjadi kesalahan jaringan DNS: {e}")
                # -----------------------------------
            else:
                print("[!] Pilihan tidak valid.")
        except KeyboardInterrupt:
            print("\n[*] Menutup aplikasi secara paksa. Sampai jumpa!")
            sys.exit(0)

def mulai_sesi_obrolan(SERVER_HOST, SERVER_PORT):
    while True:
        USERNAME = input("Masukkan Username Anda: ").strip()
        if USERNAME: break
        print("Username tidak boleh kosong!")

    print(f"\n[*] Menyiapkan koneksi ke {SERVER_HOST}:{SERVER_PORT}...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Optional bind to force Wi-Fi adapter (bypassing WSL/VMs)
    ip_asli_klien = dapatkan_ip_lokal()
    try:
        client_socket.bind((ip_asli_klien, 0)) 
    except:
        pass

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
        print(f"\n[!] Error jaringan: {e}")
        client_socket.close()
        return

    def receive_messages():
        nonlocal koneksi_aktif
        while koneksi_aktif:
            try:
                message, _ = client_socket.recvfrom(1024)
                pesan_masuk = message.decode('utf-8')
                
                if pesan_masuk == "__SERVER_STOP__":
                    print("\n\n[!] KONEKSI TERPUTUS: Server telah dimatikan oleh Admin.")
                    print("[!] Tekan ENTER untuk kembali ke Menu Utama.")
                    koneksi_aktif = False
                    break
                    
                if "[DITOLAK]" in pesan_masuk:
                    print(f"\n\n{pesan_masuk}")
                    print("[!] Tekan ENTER untuk kembali ke Menu Utama.")
                    koneksi_aktif = False
                    break
                    
                print(f"\r{pesan_masuk}\n[{USERNAME}]> ", end="", flush=True)
                
            except socket.timeout:
                continue 
            except Exception:
                if koneksi_aktif:
                    print("\n[!] Terputus dari server secara tidak terduga.")
                    koneksi_aktif = False
                break

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    print("\n" + "="*30)
    print(" SELAMAT DATANG DI RUANG OBROLAN ")
    print(" [INFO] Tekan 'Ctrl + C' untuk keluar dari server ini.")
    print("="*30 + "\n")

    while koneksi_aktif:
        try:
            pesan_keluar = input(f"[{USERNAME}]> ")
            if not koneksi_aktif: break 
            if pesan_keluar.strip(): 
                client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                
        except KeyboardInterrupt:
            print("\n\n[*] Meninggalkan ruang obrolan...")
            try:
                client_socket.sendto("__KELUAR__".encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            except: pass
            koneksi_aktif = False
            break 

    client_socket.close()
    print("[*] Sesi obrolan ditutup. Memuat ulang menu...")

if __name__ == "__main__":
    jalankan_menu_utama()