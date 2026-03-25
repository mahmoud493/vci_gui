"""ui/diagnostic/diag_panel.py — Diagnostic tab container."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.diagnostic.dtc_view          import DTCView
from ui.diagnostic.live_data_view    import LiveDataView
from ui.diagnostic.actuator_test_view import ActuatorTestView

class DiagPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.addTab(DTCView(),           "FAULT CODES")
        tabs.addTab(LiveDataView(),      "LIVE DATA")
        tabs.addTab(ActuatorTestView(),  "ACTUATOR TESTS")
        layout.addWidget(tabs)
