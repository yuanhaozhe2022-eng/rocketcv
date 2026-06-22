import sys
import math
from PyQt6.QtWidgets import QApplication, QFileDialog
from ui import RocketUI
from reader import read_dxf
from translation import analyze
from parts import Body, Fin, Rocket
from rocketstats import RocketStats


class App(RocketUI):

    def __init__(self):
        super().__init__()
        self.rocket = Rocket()
        self.stats  = RocketStats(self.rocket)
        self._sweep_updating = False   # guard against recursive sweep signals

        # ---- button connections ----
        self.button_body.clicked.connect(self.load_body)
        self.button_fin.clicked.connect(self.load_fin)

        # ---- slider / textbox sync ----
        self.fin_distance_slider.valueChanged.connect(self._slider_changed)
        self.fin_distance.editingFinished.connect(self._distance_text_changed)

        # ---- body fields ----
        self.wall.editingFinished.connect(self._recalc)
        self.density.editingFinished.connect(self._recalc)

        # ---- fin count ----
        self.fin_count.editingFinished.connect(self._fin_count_changed)

        # ---- editable fin geometry fields ----
        self.fin_root_chord.editingFinished.connect(self._fin_field_changed)
        self.fin_tip_chord.editingFinished.connect(self._fin_field_changed)
        self.fin_height.editingFinished.connect(self._fin_field_changed)
        self.fin_area.editingFinished.connect(self._fin_field_changed)
        self.fin_thickness.editingFinished.connect(self._fin_field_changed)

        # sweep_length and sweep_angle are interdependent
        self.fin_sweep_length.editingFinished.connect(self._sweep_length_changed)
        self.fin_sweep_angle.editingFinished.connect(self._sweep_angle_changed)


    # ================================================================ loading

    def load_body(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Open Body DXF", "", "DXF Files (*.dxf)")
        if not file:
            return

        data         = read_dxf(file)
        self.rocket.body = analyze(data, Body())
        body         = self.rocket.body

        self.update_body(body)
        self.update_preview_body(body)

        # enable distance controls and reset to 0
        self.fin_distance.setEnabled(True)
        self.fin_distance_slider.setEnabled(True)
        self._apply_distance(0, sync_slider=True)
        self._recalc()


    def load_fin(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Open Fin DXF", "", "DXF Files (*.dxf)")
        if not file:
            return

        data = read_dxf(file)
        fin  = analyze(data, Fin())

        # keep user-entered count if present
        try:
            fin.count = max(1, int(self.fin_count.text()))
        except ValueError:
            pass

        fin.distance_from_bottom = self._current_distance()
        self.rocket.set_fin(fin)

        self.update_fins(fin)
        self.update_preview_fin(fin)
        self.preview.set_fin_distance(fin.distance_from_bottom)
        self._recalc()


    # ================================================================ fin distance

    def _slider_changed(self, value):
        if not self.rocket.body:
            return
        # slider 1000 = distance 0; 0 = −body_length; 2000 = +body_length
        distance = (value - 1000) / 1000.0 * self.rocket.body.length
        self._apply_distance(distance, sync_slider=False)

    def _distance_text_changed(self):
        try:
            distance = float(self.fin_distance.text())
        except ValueError:
            return
        self._apply_distance(distance, sync_slider=True)

    def _apply_distance(self, distance, sync_slider=True):
        # clamp to ±body_length if body is loaded
        if self.rocket.body and self.rocket.body.length:
            L = self.rocket.body.length
            distance = max(-L, min(distance, L))

        if self.rocket.fin:
            self.rocket.fin.distance_from_bottom = distance

        self.fin_distance.setText(f"{distance:.2f}")
        self.preview.set_fin_distance(distance)

        if sync_slider and self.rocket.body and self.rocket.body.length:
            L      = self.rocket.body.length
            slider = int((distance / L) * 1000 + 1000)
            slider = max(0, min(2000, slider))
            self.fin_distance_slider.blockSignals(True)
            self.fin_distance_slider.setValue(slider)
            self.fin_distance_slider.blockSignals(False)

        self._recalc()

    def _current_distance(self):
        try:
            return float(self.fin_distance.text())
        except ValueError:
            return 0.0


    # ================================================================ editable fin fields

    def _fin_count_changed(self):
        if not self.rocket.fin:
            return
        try:
            self.rocket.fin.count = max(1, int(self.fin_count.text()))
        except ValueError:
            return
        self.update_preview_fin(self.rocket.fin)
        self._recalc()

    def _fin_field_changed(self):
        fin = self.rocket.fin
        if fin is None:
            return
        fin.root_chord  = self._read_float(self.fin_root_chord,  fin.root_chord)
        fin.tip_chord   = self._read_float(self.fin_tip_chord,   fin.tip_chord)
        fin.height      = self._read_float(self.fin_height,      fin.height)
        fin.area        = self._read_float(self.fin_area,        fin.area)
        fin.thickness   = self._read_float(self.fin_thickness,   fin.thickness)
        self._recalc()

    def _sweep_length_changed(self):
        if self._sweep_updating:
            return
        fin = self.rocket.fin
        if fin is None:
            return
        fin.sweep_length = self._read_float(self.fin_sweep_length, fin.sweep_length)
        if fin.sweep_length is not None and fin.height:
            angle = math.degrees(math.atan2(fin.sweep_length, fin.height))
            fin.sweep_angle = angle
            self._sweep_updating = True
            self.fin_sweep_angle.setText(f"{angle:.4f}")
            self._sweep_updating = False
        self._recalc()

    def _sweep_angle_changed(self):
        if self._sweep_updating:
            return
        fin = self.rocket.fin
        if fin is None:
            return
        fin.sweep_angle = self._read_float(self.fin_sweep_angle, fin.sweep_angle)
        if fin.sweep_angle is not None and fin.height:
            sweep = math.tan(math.radians(fin.sweep_angle)) * fin.height
            fin.sweep_length = sweep
            self._sweep_updating = True
            self.fin_sweep_length.setText(f"{sweep:.4f}")
            self._sweep_updating = False
        self._recalc()

    @staticmethod
    def _read_float(widget, fallback):
        try:
            return float(widget.text())
        except ValueError:
            return fallback


    # ================================================================ CG / CP

    def _recalc(self):
        self.stats.compute(
            self.wall.text(),
            self.density.text(),
            self.fin_thickness.text()
        )
        self.preview.set_cg_cp(self.stats.cg, self.stats.cp)


app    = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec())
