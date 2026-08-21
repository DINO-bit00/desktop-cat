"""
Custom Alarm Dialog
A clean, modern Qt modal dialog for setting a custom reminder.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QPushButton, QFrame, QLineEdit
)

class CustomAlarmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("? Setel Pengingat")
        self.setFixedWidth(360)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e222b;
                color: #e2e8f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 13px;
            }
            QLabel#headerTitle {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#headerSubtitle {
                font-size: 12px;
                color: #94a3b8;
            }
            QSpinBox, QLineEdit {
                background-color: #0f172a;
                color: #ffffff;
                border: 1.5px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: bold;
                min-height: 28px;
            }
            QSpinBox:focus, QLineEdit:focus {
                border-color: #38bdf8;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background: #1e293b;
                border-radius: 3px;
                margin: 2px;
            }
            QPushButton#btnStart {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#btnStart:hover {
                background-color: #2563eb;
            }
            QPushButton#btnStart:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#btnCancel {
                background-color: #334155;
                color: #cbd5e1;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton#btnCancel:hover {
                background-color: #475569;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        title = QLabel("? Pengingat Kustom", self)
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        subtitle = QLabel("Kucing akan mengingatkanmu ke tengah layar saat waktunya tiba.", self)
        subtitle.setObjectName("headerSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #334155;")
        layout.addWidget(divider)

        # Field 1: Minutes
        layout.addWidget(QLabel("? <b>Berapa menit lagi?</b>", self))
        self.spin_minutes = QSpinBox(self)
        self.spin_minutes.setRange(1, 240)
        self.spin_minutes.setValue(30)
        self.spin_minutes.setSuffix(" Menit")
        layout.addWidget(self.spin_minutes)

        # Field 2: Message
        layout.addWidget(QLabel("?? <b>Pesan Pengingat:</b>", self))
        self.input_msg = QLineEdit(self)
        self.input_msg.setPlaceholderText("Contoh: Cek email dari bos")
        layout.addWidget(self.input_msg)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("?? Setel Alarm", self)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def get_values(self):
        """Returns (minutes, message)."""
        msg = self.input_msg.text().strip()
        if not msg:
            msg = "Waktunya habis! Ada hal penting yang harus kamu lakukan."
        return (self.spin_minutes.value(), msg)

