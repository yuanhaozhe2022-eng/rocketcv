from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from preview import DXFPreview


class RocketUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RoCv v0.15")
        self.setMinimumSize(1000, 640)
        self._setup()


    def _setup(self):

        # ---- preview ----
        self.preview = DXFPreview()
        self.preview.setMinimumSize(500, 500)

        # ---- slider (vertical, beside preview) ----
        # Range 0-2000, default 1000 (centre = fin distance 0).
        # Value > 1000 → fin moves toward nose; < 1000 → toward / below tail.
        self.fin_distance_slider = QSlider(Qt.Orientation.Vertical)
        self.fin_distance_slider.setRange(0, 2000)
        self.fin_distance_slider.setValue(1000)
        self.fin_distance_slider.setEnabled(False)
        self.fin_distance_slider.setFixedWidth(30)

        slider_col = QVBoxLayout()
        slider_col.addWidget(QLabel("▲ Nose"), 0, Qt.AlignmentFlag.AlignHCenter)
        slider_col.addWidget(self.fin_distance_slider, 1)
        slider_col.addWidget(QLabel("▼ Tail"), 0, Qt.AlignmentFlag.AlignHCenter)

        # ---- side panel (scrollable) ----
        side_widget = QWidget()
        side        = QVBoxLayout(side_widget)
        side.setSpacing(3)
        side.setContentsMargins(4, 4, 4, 4)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet("font-weight: bold; margin-top: 6px;")
            return l

        def field():
            f = QLineEdit()
            f.setFixedHeight(24)
            return f

        # -- Body --
        side.addWidget(lbl("── Body ──"))
        side.addWidget(QLabel("Length (auto)"))
        self.length = field()
        side.addWidget(self.length)

        side.addWidget(QLabel("Diameter (auto)"))
        self.diameter = field()
        side.addWidget(self.diameter)

        side.addWidget(QLabel("Wall Thickness"))
        self.wall = field()
        side.addWidget(self.wall)

        side.addWidget(QLabel("Density (g/cm³ or kg/m³)"))
        self.density = field()
        side.addWidget(self.density)

        self.button_body = QPushButton("Upload Body DXF")
        side.addWidget(self.button_body)
        self.body_info = QLabel("Body: none")
        side.addWidget(self.body_info)

        # -- Fin --
        side.addWidget(lbl("── Fins ──"))

        side.addWidget(QLabel("Fin Count"))
        self.fin_count = field()
        side.addWidget(self.fin_count)

        side.addWidget(QLabel("Fin Distance from Bottom"))
        self.fin_distance = field()
        self.fin_distance.setEnabled(False)
        side.addWidget(self.fin_distance)

        side.addWidget(lbl("  Fin Geometry"))

        side.addWidget(QLabel("Root Chord"))
        self.fin_root_chord = field()
        side.addWidget(self.fin_root_chord)

        side.addWidget(QLabel("Tip Chord"))
        self.fin_tip_chord = field()
        side.addWidget(self.fin_tip_chord)

        side.addWidget(QLabel("Height / Span"))
        self.fin_height = field()
        side.addWidget(self.fin_height)

        side.addWidget(QLabel("Sweep Length"))
        self.fin_sweep_length = field()
        side.addWidget(self.fin_sweep_length)

        side.addWidget(QLabel("Sweep Angle (°)"))
        self.fin_sweep_angle = field()
        side.addWidget(self.fin_sweep_angle)

        side.addWidget(QLabel("Fin Area (auto)"))
        self.fin_area = field()
        side.addWidget(self.fin_area)

        side.addWidget(QLabel("Fin Thickness"))
        self.fin_thickness = field()
        side.addWidget(self.fin_thickness)

        self.button_fin = QPushButton("Upload Fin DXF")
        side.addWidget(self.button_fin)
        self.fin_info = QLabel("Fin: none")
        side.addWidget(self.fin_info)

        side.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidget(side_widget)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(240)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # ---- main layout ----
        root = QHBoxLayout(self)
        root.addWidget(self.preview, stretch=1)
        root.addLayout(slider_col)
        root.addWidget(scroll)


    # ------------------------------------------------------------------ update helpers

    def update_body(self, body):
        self.body_info.setText(f"Body: L={body.length:.1f}  D={body.diameter:.1f}")
        self.length.setText(f"{body.length:.4f}")
        self.diameter.setText(f"{body.diameter:.4f}")

    def update_fins(self, fin):
        self.fin_info.setText(f"Fin: {fin.count}× {fin.width:.1f}×{fin.height:.1f}" if fin.width else "Fin: loaded")

        def fmt(v):
            return f"{v:.4f}" if v is not None else ""

        self.fin_root_chord.setText(fmt(fin.root_chord))
        self.fin_tip_chord.setText(fmt(fin.tip_chord))
        self.fin_height.setText(fmt(fin.height))
        self.fin_sweep_length.setText(fmt(fin.sweep_length))
        self.fin_sweep_angle.setText(fmt(fin.sweep_angle))
        self.fin_area.setText(fmt(fin.area))

    def update_preview_body(self, body):
        self.preview.set_body(body.length, body.diameter)

    def update_preview_fin(self, fin):
        canon = fin.canonical_geometry or []
        span  = fin.height or 0
        self.preview.set_fin(canon, span, fin.count)
