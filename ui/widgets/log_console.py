"""ui/widgets/log_console.py — ANSI-coloured log console widget."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel
from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QTextCursor, QColor, QFont
from app.event_bus import bus

LEVEL_COLORS = {
    "DEBUG": "#4a6680",
    "INFO":  "#5af078",
    "WARN":  "#ffb300",
    "ERROR": "#ff3a3a",
    "CRIT":  "#ff0055",
}

class LogConsole(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._max_lines = 2000
        self._paused    = False
        self._setup_ui()
        bus.log_message.connect(self._on_log)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(2)
        # ✅ Créer le log AVANT
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 10))
        self._log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        # Toolbar
        bar = QHBoxLayout()
        lbl = QLabel("CONSOLE")
        lbl.setObjectName("label_section")
        bar.addWidget(lbl)
        bar.addStretch()

        self._filter = QComboBox()
        self._filter.addItems(["ALL", "DEBUG", "INFO", "WARN", "ERROR"])
        self._filter.setFixedWidth(90)
        bar.addWidget(self._filter)

        self._btn_pause = QPushButton("PAUSE")
        self._btn_pause.setFixedWidth(70)
        self._btn_pause.clicked.connect(self._toggle_pause)
        bar.addWidget(self._btn_pause)

        btn_clear = QPushButton("CLEAR")
        btn_clear.setFixedWidth(70)
        btn_clear.clicked.connect(self._log.clear)
        bar.addWidget(btn_clear)

        root.addLayout(bar)

        # Text area
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("Consolas", 10))
        self._log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        root.addWidget(self._log)

    @pyqtSlot(str, str)
    def _on_log(self, level: str, text: str):
        if self._paused:
            return
        min_level = self._filter.currentText()
        levels_order = ["DEBUG", "INFO", "WARN", "ERROR", "CRIT"]
        if min_level != "ALL":
            if levels_order.index(level) < levels_order.index(min_level):
                return

        color = LEVEL_COLORS.get(level, "#c8d0dc")
        html  = (f'<span style="color:{LEVEL_COLORS.get(level,"#4a6680")}">[{level:5s}]</span>'
                 f' <span style="color:{color}">{text}</span><br>')
        self._log.moveCursor(QTextCursor.MoveOperation.End)
        self._log.insertHtml(html)

        # Trim
        doc = self._log.document()
        while doc.blockCount() > self._max_lines:
            cur = QTextCursor(doc)
            cur.select(QTextCursor.SelectionType.BlockUnderCursor)
            cur.removeSelectedText()
            cur.deleteChar()

        self._log.moveCursor(QTextCursor.MoveOperation.End)

    def _toggle_pause(self):
        self._paused = not self._paused
        self._btn_pause.setText("RESUME" if self._paused else "PAUSE")
