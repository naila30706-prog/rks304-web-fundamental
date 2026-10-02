import socket
from abc import ABC, abstractmethod
from datetime import datetime


class BaseScanner(ABC):
    """Kelas abstrak untuk semua jenis pemindai jaringan."""

    def __init__(self, host, start_port, end_port, timeout=0.4):
        # Atribut protected (enkapsulasi)
        self._host = host
        self._start_port = start_port
        self._end_port = end_port
        self._timeout = timeout
        self._target_ip = None
        self._open_ports = []
        self._scan_time = None

    # Antarmuka publik (read-only) untuk mengakses data
    @property
    def host(self):
        return self._host

    @property
    def target_ip(self):
        return self._target_ip

    @property
    def start_port(self):
        return self._start_port

    @property
    def end_port(self):
        return self._end_port

    @property
    def open_ports(self):
        return list(self._open_ports)  # salinan, data asli tetap aman

    @property
    def scan_time(self):
        return self._scan_time

    @abstractmethod
    def scan(self):
        """Wajib diimplementasikan oleh kelas turunan."""
        pass


class TCPPortScanner(BaseScanner):
    """Pemindai port khusus protokol TCP."""

    def _resolve_host(self):
        """Mengubah nama host menjadi alamat IP."""
        try:
            self._target_ip = socket.gethostbyname(self._host)
        except socket.gaierror:
            raise ValueError("Host tidak dapat diselesaikan. Periksa kembali nama/IP target.")

    def scan(self):
        """Memindai port TCP dan mengembalikan daftar port terbuka."""
        self._resolve_host()
        self._open_ports = []
        self._scan_time = datetime.now()

        print("-" * 50)
        print(f" Memindai Target IP: {self._target_ip}")
        print(f" Rentang Port      : {self._start_port} - {self._end_port}")
        print(f" Waktu Mulai       : {self._scan_time}")
        print("-" * 50)

        try:
            for port in range(self._start_port, self._end_port + 1):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self._timeout)
                result = s.connect_ex((self._target_ip, port))
                s.close()

                if result == 0:
                    print(f"[+] Port {port} : TERBUKA")
                    self._open_ports.append(port)
        except KeyboardInterrupt:
            print("\n[!] Pemindaian dibatalkan oleh pengguna (Ctrl+C).")

        print("-" * 50)
        print(f" Pemindaian Selesai. Total port terbuka ditemukan: {len(self._open_ports)}")
        print("-" * 50)

        return self.open_ports