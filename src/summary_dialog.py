import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt


class DailySummaryDialog(QDialog):
    """
    Daily Productivity Summary Dialog (Feature 25).
    Displays a retro pixel art dashboard summarizing focus time, Pomodoro cycles,
    hydration/stretch wellness, and cat companion interactions.
    """
    def __init__(self, stats: dict = None, pet_name: str = "NyangBuddy", affection_pts: int = 50, parent=None):
        super().__init__(parent)
        self.stats = stats or {}
        self.pet_name = pet_name
        self.affection_pts = affection_pts

        self.setWindowTitle(f"📊 Rekap Produktivitas Harian — {self.pet_name}")
        self.setFixedWidth(420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._init_ui()
        self._apply_styling()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        # Header Title
        title_lbl = QLabel(f"🌟 Laporan Harian Produktivitas")
        title_lbl.setObjectName("summaryTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        sub_lbl = QLabel(f"Pendamping Kerja: <b>{self.pet_name}</b> 🐾")
        sub_lbl.setObjectName("summarySub")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_lbl)

        # Metrics Card Grid
        grid_frame = QFrame()
        grid_frame.setObjectName("gridCard")
        grid = QGridLayout(grid_frame)
        grid.setContentsMargins(14, 14, 14, 14)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        pom_count = self.stats.get("pomodoro_completed", 0)
        focus_mins = pom_count * 25
        hours = focus_mins // 60
        mins = focus_mins % 60
        time_str = f"{hours}j {mins}m" if hours > 0 else f"{mins} menit"

        water_count = self.stats.get("hydration_count", 0)
        stretch_count = self.stats.get("stretch_count", 0)
        food_count = self.stats.get("food_count", 0)

        metrics = [
            ("⏱️ Total Waktu Fokus", time_str, "#38bdf8"),
            ("🎯 Siklus Pomodoro", f"{pom_count} siklus", "#34d399"),
            ("💧 Minum Air Putih", f"{water_count} gelas", "#60a5fa"),
            ("🧘 Peregangan Otot", f"{stretch_count} sesi", "#a78bfa"),
            ("🐟 Snack Diberikan", f"{food_count} snack", "#fbbf24"),
            ("💖 Level Kasih Sayang", f"{self.affection_pts}/100 Poin", "#f472b6"),
        ]

        row, col = 0, 0
        for title, val, color in metrics:
            box = QFrame()
            box.setObjectName("metricBox")
            b_lay = QVBoxLayout(box)
            b_lay.setContentsMargins(8, 8, 8, 8)
            b_lay.setSpacing(2)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")

            b_lay.addWidget(t_lbl)
            b_lay.addWidget(v_lbl)
            grid.addWidget(box, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addWidget(grid_frame)

        # Pet Evaluation Banner
        eval_frame = QFrame()
        eval_frame.setObjectName("evalCard")
        eval_lay = QVBoxLayout(eval_frame)
        eval_lay.setContentsMargins(12, 10, 12, 10)
        eval_lay.setSpacing(4)

        if pom_count >= 4:
            eval_text = "🔥 Luar biasa produktif! Kamu menuntaskan target fokus hari ini dengan sangat hebat, boss! Jangan lupa istirahat cukup ya~ ✨"
        elif pom_count >= 1:
            eval_text = "✨ Kerja bagus hari ini! Sesi fokus berjalan lancar dan tubuh tetap terawat dengan baik nya~ 🐾"
        else:
            eval_text = "🐾 Hari yang santai! Siap memulai sesi fokus baru kapan pun kamu siap, aku selalu di sampingmu nya~ 💻"

        eval_lbl = QLabel(eval_text)
        eval_lbl.setWordWrap(True)
        eval_lbl.setStyleSheet("color: #e2e8f0; font-size: 12px; font-style: italic;")
        eval_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eval_lay.addWidget(eval_lbl)
        layout.addWidget(eval_frame)

        # Close Button
        btn_close = QPushButton("Tutup Rekap 🐾")
        btn_close.setObjectName("closeBtn")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _apply_styling(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0b1329;
                border: 2px solid #3b82f6;
                border-radius: 12px;
                font-family: 'Segoe UI', sans-serif;
            }
            #summaryTitle {
                color: #60a5fa;
                font-size: 17px;
                font-weight: bold;
            }
            #summarySub {
                color: #cbd5e1;
                font-size: 12px;
            }
            #gridCard {
                background-color: #131d38;
                border: 1px solid #334155;
                border-radius: 10px;
            }
            #metricBox {
                background-color: #1e293b;
                border: 1px solid #3b4252;
                border-radius: 6px;
            }
            #evalCard {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
            }
            #closeBtn {
                background-color: #3b82f6;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 9px 18px;
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
