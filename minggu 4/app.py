import socket
import sys
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def resolve_host(target_host):
    """Menyelesaikan nama host menjadi alamat IP."""
    try:
        return socket.gethostbyname(target_host)
    except socket.gaierror:
        print("\n[!] Host tidak dapat diselesaikan. Periksa kembali nama/IP target.")
        sys.exit(1)

def scan_ports(target_ip, start_port, end_port, timeout=0.5):
    """Melakukan pemindaian port TCP dan mengembalikan daftar port yang terbuka."""
    open_ports = []
    
    print("-" * 50)
    print(f" Memindai Target IP: {target_ip}")
    print(f" Rentang Port      : {start_port} - {end_port}")
    print(f" Waktu Mulai       : {str(datetime.now())}")
    print("-" * 50)

    try:
        for port in range(start_port, end_port + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((target_ip, port))
            s.close()
            
            if result == 0:
                print(f"[+] Port {port} : TERBUKA")
                open_ports.append(port)
                
    except KeyboardInterrupt:
        print("\n[!] Pemindaian dibatalkan oleh pengguna (Ctrl+C).")

    print("-" * 50)
    print(f" Pemindaian Selesai. Total port terbuka ditemukan: {len(open_ports)}")
    print("-" * 50)
    
    return open_ports

def export_to_pdf(target_host, target_ip, start_port, end_port, open_ports, filename="laporan_scan.pdf"):
    """Mengeksport hasil pemindaian ke dokumen PDF."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Kustomisasi Gaya Teks
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
        alignment=1
    )
    normal_style = styles['Normal']

    # Judul Laporan
    story.append(Paragraph("Laporan Hasil Pemindaian Port (Port Scanner)", title_style))
    story.append(Spacer(1, 12))

    # Informasi Target
    summary_data = [
        [Paragraph("<b>Target Host:</b>", normal_style), Paragraph(target_host, normal_style)],
        [Paragraph("<b>Target IP:</b>", normal_style), Paragraph(target_ip, normal_style)],
        [Paragraph("<b>Rentang Port:</b>", normal_style), Paragraph(f"{start_port} - {end_port}", normal_style)],
        [Paragraph("<b>Waktu Eksekusi:</b>", normal_style), Paragraph(str(datetime.now()), normal_style)],
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 380])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f7fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Tabel Hasil Port Terbuka
    story.append(Paragraph("<b>Daftar Port Terbuka</b>", styles['Heading2']))
    story.append(Spacer(1, 6))

    if open_ports:
        port_table_data = [["Port", "Status", "Layanan Umum (Estimasi)"]]
        for p in open_ports:
            service = "HTTP/HTTPS" if p in [80, 443] else ("SSH" if p == 22 else ("FTP" if p == 21 else "Lainnya/Custom"))
            port_table_data.append([str(p), "TERBUKA", service])
        
        p_table = Table(port_table_data, colWidths=[100, 150, 250])
        p_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(p_table)
    else:
        story.append(Paragraph("Tidak ada port terbuka yang ditemukan pada rentang tersebut.", normal_style))

    # Membangun PDF
    doc.build(story)
    print(f"[+] Laporan berhasil dieksport ke PDF: {filename}")

def export_to_json(target_host, target_ip, start_port, end_port, open_ports, filename="laporan_scan.json"):
    """Mengeksport hasil pemindaian ke dokumen JSON."""
    data = {
        "target_host": target_host,
        "target_ip": target_ip,
        "port_range": {
            "start": start_port,
            "end": end_port
        },
        "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_open_ports": len(open_ports),
        "open_ports": [
            {
                "port": p,
                "status": "OPEN",
                "estimated_service": "HTTP/HTTPS" if p in [80, 443] else ("SSH" if p == 22 else ("FTP" if p == 21 else "Lainnya/Custom"))
            }
            for p in open_ports
        ]
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[+] Laporan berhasil dieksport ke JSON: {filename}")

def main():
    print("=== APLIKASI PORT SCANNER & EXPORTER (PROSEDURAL) ===")
    target = input("Masukkan IP atau Domain target (contoh: 127.0.0.1): ").strip()
    
    try:
        start = int(input("Masukkan port awal (contoh: 1): "))
        end = int(input("Masukkan port akhir (contoh: 1024): "))
    except ValueError:
        print("[!] Masukkan angka port yang valid.")
        sys.exit(1)

    # 1. Resolusi Host ke IP
    target_ip = resolve_host(target)

    # 2. Jalankan proses pemindaian port
    open_ports = scan_ports(target_ip, start, end, timeout=0.4)
    
    # 3. Ekspor hasil ke PDF dan JSON
    safe_target = target.replace('.', '_')
    pdf_filename = f"scan_report_{safe_target}.pdf"
    json_filename = f"scan_report_{safe_target}.json"

    export_to_pdf(target, target_ip, start, end, open_ports, filename=pdf_filename)
    export_to_json(target, target_ip, start, end, open_ports, filename=json_filename)

if __name__ == "__main__":
    main()