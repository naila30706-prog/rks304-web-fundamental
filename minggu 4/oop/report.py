import json
from abc import ABC, abstractmethod

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class BaseReportExporter(ABC):
    """Kelas abstrak untuk semua jenis pengekspor laporan."""

    SERVICES = {21: "FTP", 22: "SSH", 80: "HTTP/HTTPS", 443: "HTTP/HTTPS"}

    def __init__(self, scanner, filename):
        # Atribut private (enkapsulasi data agregasi dan nama berkas)
        self.__scanner = scanner
        self.__filename = filename

    @property
    def filename(self):
        return self.__filename

    @property
    def scanner(self):
        return self.__scanner

    def _get_service(self, port):
        return self.SERVICES.get(port, "Lainnya/Custom")

    @abstractmethod
    def export(self):
        """Wajib diimplementasikan oleh kelas turunan."""
        pass


class PDFReportExporter(BaseReportExporter):
    """Mengekspor hasil pemindaian ke PDF."""

    def export(self):
        sc = self.scanner
        doc = SimpleDocTemplate(self.filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        normal = styles["Normal"]

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a365d"),
            spaceAfter=12,
            alignment=1,
        )

        story.append(Paragraph("Laporan Hasil Pemindaian Port (Port Scanner)", title_style))
        story.append(Spacer(1, 12))

        summary_data = [
            [Paragraph("<b>Target Host:</b>", normal), Paragraph(sc.host, normal)],
            [Paragraph("<b>Target IP:</b>", normal), Paragraph(sc.target_ip, normal)],
            [Paragraph("<b>Rentang Port:</b>", normal), Paragraph(f"{sc.start_port} - {sc.end_port}", normal)],
            [Paragraph("<b>Waktu Eksekusi:</b>", normal), Paragraph(str(sc.scan_time), normal)],
        ]
        summary_table = Table(summary_data, colWidths=[120, 380])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>Daftar Port Terbuka</b>", styles["Heading2"]))
        story.append(Spacer(1, 6))

        if sc.open_ports:
            data = [["Port", "Status", "Layanan Umum (Estimasi)"]]
            for p in sc.open_ports:
                data.append([str(p), "TERBUKA", self._get_service(p)])

            table = Table(data, colWidths=[100, 150, 250])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ffffff")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Tidak ada port terbuka yang ditemukan pada rentang tersebut.", normal))

        doc.build(story)
        print(f"[+] Laporan berhasil dieksport ke PDF: {self.filename}")


class JSONReportExporter(BaseReportExporter):
    """Mengekspor hasil pemindaian ke JSON."""

    def export(self):
        sc = self.scanner
        data = {
            "target_host": sc.host,
            "target_ip": sc.target_ip,
            "port_range": {"start": sc.start_port, "end": sc.end_port},
            "scan_time": sc.scan_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_open_ports": len(sc.open_ports),
            "open_ports": [
                {"port": p, "status": "OPEN", "estimated_service": self._get_service(p)}
                for p in sc.open_ports
            ],
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[+] Laporan berhasil dieksport ke JSON: {self.filename}")