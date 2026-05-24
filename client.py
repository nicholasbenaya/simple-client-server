import socket
import threading
import sys

def jalankan_menu_utama():
    while True:
        print("\n" + "="*40)
        print("           MENU UTAMA KLIEN           ")
        print("="*40)
        print("1. Hubungkan ke Server Lokal (Simulasi)")
        print("2. Hubungkan ke Server Teman (LAN/Wi-Fi)")
        print("3. Keluar dari Program")
        
        try:
            pilihan = input("Pilih menu (1/2/3): ").strip()
            
            if pilihan == '3':
                print("[*] Terima kasih telah menggunakan aplikasi ini. Sampai jumpa!")
                sys.exit(0) # Ini adalah satu-satunya cara keluar dari aplikasi
            elif pilihan in ['1', '2']:
                mulai_sesi_obrolan(pilihan) # Masuk ke ruang obrolan
            else:
                print("[!] Pilihan tidak valid.")
        except KeyboardInterrupt:
            # Jika user menekan Ctrl+C di menu utama
            print("\n[*] Menutup aplikasi secara paksa. Sampai jumpa!")
            sys.exit(0)

# Fungsi utama untuk satu sesi obrolan
def mulai_sesi_obrolan(mode_jaringan):
    if mode_jaringan == '1':
        SERVER_HOST = '127.0.0.1'
    else:
        SERVER_HOST = input("Masukkan IP Server: ").strip()

    port_input = input("Masukkan Port Server (misal 5000): ").strip()
    SERVER_PORT = int(port_input) if port_input.isdigit() else 5000

    while True:
        USERNAME = input("Masukkan Username Anda: ").strip()
        if USERNAME: break
        print("Username tidak boleh kosong!")

    print(f"\n[*] Menyiapkan koneksi ke {SERVER_HOST}:{SERVER_PORT}...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    koneksi_aktif = True # Bendera (Flag) pengatur jalannya obrolan

    # --- HANDSHAKE (Validasi Koneksi) ---
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
            return # Menghentikan fungsi obrolan dan kembali ke Main Menu

        client_socket.settimeout(1.0) # Set timeout kecil agar thread bisa mendeteksi bendera dengan cepat
    except socket.timeout:
        print("\n[!] Gagal terhubung: Server tidak merespons.")
        client_socket.close()
        return
    except Exception as e:
        print(f"\n[!] Error jaringan: {e}")
        client_socket.close()
        return

    # --- FUNGSI PENDENGAR PESAN ---
    def receive_messages():
        nonlocal koneksi_aktif
        while koneksi_aktif:
            try:
                message, _ = client_socket.recvfrom(1024)
                pesan_masuk = message.decode('utf-8')
                
                # FITUR 2: Server meminta klien putus
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
                continue # Ini normal karena timeout di-set 1.0, biarkan memutar loop lagi
            except Exception:
                if koneksi_aktif:
                    print("\n[!] Terputus dari server secara tidak terduga.")
                    koneksi_aktif = False
                break

    # Jalankan thread
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    # --- ANTARMUKA KLIEN ---
    print("\n" + "="*30)
    print(" SELAMAT DATANG DI RUANG OBROLAN ")
    # FITUR 1: Instruksi Hotkey ditampilkan dengan jelas
    print(" [INFO] Tekan 'Ctrl + C' untuk keluar dari server ini.")
    print("="*30 + "\n")

    # Loop pengetikan
    while koneksi_aktif:
        try:
            pesan_keluar = input(f"[{USERNAME}]> ")
            
            # Jika user menekan ENTER sesaat setelah server mati (bendera False)
            if not koneksi_aktif:
                break 

            # Mengirim pesan normal, kata 'keluar' tetap akan dikirim sebagai obrolan biasa
            if pesan_keluar.strip(): 
                client_socket.sendto(pesan_keluar.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
                
        except KeyboardInterrupt:
            # FITUR 1: Menangkap Kombinasi Tombol Ctrl+C
            print("\n\n[*] Meninggalkan ruang obrolan...")
            try:
                # Memberi tahu server bahwa kita pergi
                client_socket.sendto("__KELUAR__".encode('utf-8'), (SERVER_HOST, SERVER_PORT))
            except:
                pass
            koneksi_aktif = False
            break # Keluar dari loop chat, lalu fungsi ini selesai, otomatis kembali ke Menu Utama

    # Pembersihan Sesi
    client_socket.close()
    print("[*] Sesi obrolan ditutup. Memuat ulang menu...")

# Menjalankan keseluruhan aplikasi
if __name__ == "__main__":
    jalankan_menu_utama()