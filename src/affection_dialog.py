import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class AffectionDialog(QDialog):
    """
    Cute Retro Pixel Art Affection & Mood Status Dialog (Feature 23).
    Displays affection level, mood status, stats (snacks, petting, pomodoros),
    and motivational pet messages.
    """
    def __init__(self, affection_pts: int = 50, stats: dict = None, pet_name: str = "NyangBuddy", parent=None):
        super().__init__(parent)
        self.affection_pts = max(0, min(100, affection_pts))
        self.stats = stats or {}
        self.pet_name = pet_name

        self.setWindowTitle(f"💖 Status Kasih Sayang — {self.pet_name}")
        self.setFixedWidth(380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._init_ui()
        self._apply_styling()

    def _get_rank_info(self, pts: int):
        if pts >= 100:
            return "👑 Sahabat Sejati (Soulmate)", "Kucing ini menganggapmu sebagai keluarga tercinta! Hubungan kalian tak terpisahkan nya! 🌟❤️"
        elif pts >= 75:
            return "🌟 Sahabat Dekat (Best Friend)", "Kucing ini sangat menyayangimu dan selalu bersemangat menemanimu bekerja! 🐾💖"
        elif pts >= 50:
            return "💖 Teman Akrab (Close Buddy)", "Kalian sudah saling mengenal dekat dan senang menghabiskan waktu bersama! 😸✨"
        elif pts >= 25:
            return "😸 Teman Baru (Good Pal)", "Kucing mulai merasa nyaman dan selalu menyambutmu dengan ceria! 🐾"
        else:
            return "🐾 Kucing Pemalu (Shy Kitten)", "Kucing masih sedikit pemalu, sering-sering dielus dan diberi snack ya nya~ 🐟"

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title Banner
        title_lbl = QLabel(f"🐱 Profil Afeksi {self.pet_name}")
        title_lbl.setObjectName("dialogTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        rank_title, rank_desc = self._get_rank_info(self.affection_pts)

        # Rank Badge
        rank_box = QFrame()
        rank_box.setObjectName("rankBox")
        rank_layout = QVBoxLayout(rank_box)
        rank_layout.setContentsMargins(12, 10, 12, 10)
        rank_layout.setSpacing(4)

        rank_lbl = QLabel(rank_title)
        rank_lbl.setObjectName("rankTitle")
        rank_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_layout.addWidget(rank_lbl)

        desc_lbl = QLabel(rank_desc)
        desc_lbl.setObjectName("rankDesc")
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_layout.addWidget(desc_lbl)
        layout.addWidget(rank_box)

        # Progress Bar
        bar_layout = QVBoxLayout()
        bar_layout.setSpacing(4)
        bar_header = QHBoxLayout()
        pts_label = QLabel("Tingkat Kedekatan:")
        pts_label.setStyleSheet("color: #cbd5e1; font-weight: bold;")
        val_label = QLabel(f"{self.affection_pts} / 100 Poin")
        val_label.setStyleSheet("color: #f472b6; font-weight: bold;")
        bar_header.addWidget(pts_label)
        bar_header.addStretch()
        bar_header.addWidget(val_label)
        bar_layout.addLayout(bar_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(self.affection_pts)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(16)
        bar_layout.addWidget(self.progress_bar)
        layout.addLayout(bar_layout)

        # Activity Stats Box
        stats_box = QFrame()
        stats_box.setObjectName("statsBox")
        stats_layout = QVBoxLayout(stats_box)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(6)

        food_count = self.stats.get("food_count", 0)
        pet_count = self.stats.get("pet_count", 0)
        pom_count = self.stats.get("pomodoro_completed", 0)

        s1 = QLabel(f"🐟 Total Diberi Makan: <b>{food_count} kali</b>")
        s2 = QLabel(f"❤️ Total Dielus / Sayang: <b>{pet_count} kali</b>")
        s3 = QLabel(f"⏱️ Siklus Pomodoro Selesai: <b>{pom_count} siklus</b>")

        for s in (s1, s2, s3):
            s.setStyleSheet("color: #e2e8f0; font-size: 12px;")
            stats_layout.addWidget(s)
        layout.addWidget(stats_box)

        # Close Button
        btn_close = QPushButton("Tutup 🐾")
        btn_close.setObjectName("closeBtn")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _apply_styling(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                border: 2px solid #3b82f6;
                border-radius: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            #dialogTitle {
                color: #60a5fa;
                font-size: 16px;
                font-weight: bold;
            }
            #rankBox {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
            }
            #rankTitle {
                color: #f59e0b;
                font-size: 14px;
                font-weight: bold;
            }
            #rankDesc {
                color: #94a3b8;
                font-size: 11px;
            }
            QProgressBar {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ec4899, stop:1 #f43f5e);
                border-radius: 7px;
            }
            #statsBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            #closeBtn {
                background-color: #3b82f6;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
            }
            #closeBtn:hover {
                background-color: #2563eb;
            }
            #closeBtn:pressed {
                background-color: #1d4ed8;
            }
        """)
