"""ui/widgets/status_bar.py — Custom bottom status bar."""
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSlot, Qt, QTimer
from app.event_bus import bus

class VCIStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        bus.connection_changed.connect(self._on_connection)
        bus.status_message.connect(self._on_status)
        bus.frame_received.connect(self._on_frame)
        self._frame_count = 0
        self._fps_timer   = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)

    def _build(self):
        self.setSizeGripEnabled(False)

        self._lbl_conn = QLabel("● DISCONNECTED")
        self._lbl_conn.setObjectName("label_err")
        self.addWidget(self._lbl_conn)

        self._sep1 = QLabel("│")
        self._sep1.setObjectName("label_section")
        self.addWidget(self._sep1)

        self._lbl_transport = QLabel("—")
        self._lbl_transport.setObjectName("label_section")
        self.addWidget(self._lbl_transport)

        self.addWidget(_spacer())

        self._lbl_fps = QLabel("0 fr/s")
        self._lbl_fps.setObjectName("label_section")
        self.addPermanentWidget(self._lbl_fps)

        self._lbl_msg = QLabel("")
        self._lbl_msg.setObjectName("label_section")
        self.addPermanentWidget(self._lbl_msg)

    @pyqtSlot(bool, str)
    def _on_connection(self, connected: bool, desc: str):
        if connected:
            self._lbl_conn.setText("● CONNECTED")
            self._lbl_conn.setObjectName("label_ok")
            self._lbl_transport.setText(desc)
        else:
            self._lbl_conn.setText("● DISCONNECTED")
            self._lbl_conn.setObjectName("label_err")
            self._lbl_transport.setText("—")
        self._lbl_conn.style().unpolish(self._lbl_conn)
        self._lbl_conn.style().polish(self._lbl_conn)

    @pyqtSlot(str)
    def _on_status(self, msg: str):
        self._lbl_msg.setText(msg)

    @pyqtSlot(object)
    def _on_frame(self, _):
        self._frame_count += 1

    def _update_fps(self):
        self._lbl_fps.setText(f"{self._frame_count} fr/s")
        self._frame_count = 0

def _spacer() -> QWidget:
    w = QWidget()
    w.setSizePolicy(w.sizePolicy().horizontalPolicy(),
                    w.sizePolicy().verticalPolicy())
    from PyQt6.QtWidgets import QSizePolicy
    w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return w
