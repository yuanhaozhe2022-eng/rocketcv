from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PyQt6.QtCore import Qt, QRect

CG_FILL    = QColor(255, 200, 0)
CG_BORDER  = QColor(150, 110, 0)
CP_FILL    = QColor(30,  110, 220)
CP_BORDER  = QColor(10,   60, 150)


class DXFPreview(QWidget):
    """
    Side-view preview of the rocket.

    Coordinate conventions
    ----------------------
    World coordinates (same units as DXF):
        x = 0 is the rocket centreline.
        y = 0 is the tail (bottom); y = body_length is the nose (top).
        Body occupies x ∈ [−d/2, +d/2], y ∈ [0, L].
        Fin (in canonical form) attaches at the left of the body:
            world_x  = −spanwise − d/2   (sticks to the left)
            world_y  = distance_from_bottom + chordwise

    So changing distance_from_bottom slides the fin UP or DOWN vertically.
    """

    def __init__(self):
        super().__init__()

        self.body_length   = None   # DXF units
        self.body_diameter = None

        # Canonical fin geometry: list of {"start":(cx,cy), "end":(cx,cy)}
        # where cx = chordwise (0 at root_back), cy = spanwise (0 at body wall)
        self.fin_canonical = []
        self.fin_span      = 0.0   # max spanwise extent  (= fin.height in canonical)
        self.fin_count     = 0

        self.distance_from_bottom = 0.0   # world_y of root_back

        self.cg_from_nose = None   # DXF units from top
        self.cp_from_nose = None

        self.unit_mm   = True        # toggle mm ↔ cm
        self._lbl_rect = None        # region that the unit label occupies


    # ------------------------------------------------------------------ setters

    def set_body(self, length, diameter):
        self.body_length   = float(length)   if length   else None
        self.body_diameter = float(diameter) if diameter else None
        self.update()

    def set_fin(self, canonical_lines, span, count):
        self.fin_canonical = canonical_lines or []
        self.fin_span      = float(span)  if span  else 0.0
        self.fin_count     = int(count)   if count else 0
        self.update()

    def set_fin_distance(self, distance):
        self.distance_from_bottom = float(distance) if distance is not None else 0.0
        self.update()

    def set_cg_cp(self, cg, cp):
        self.cg_from_nose = cg
        self.cp_from_nose = cp
        self.update()


    # ------------------------------------------------------------------ events

    def mousePressEvent(self, event):
        if self._lbl_rect and self._lbl_rect.contains(event.pos()):
            self.unit_mm = not self.unit_mm
            self.update()


    # ------------------------------------------------------------------ paint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        L = self.body_length
        d = self.body_diameter

        if not L and not self.fin_canonical:
            self._draw_labels(painter, None)
            return

        # ---- build world bounding box ----------------------------------------
        gap = max(self.fin_span * 0.15, 5.0) if self.fin_span else 5.0

        xs, ys = [], []
        if L and d:
            xs += [-d/2, d/2]
            ys += [0.0, L]

        for i in range(self.fin_count):
            x_shift = i * (self.fin_span + gap)
            for seg in self.fin_canonical:
                for (cx, cy) in (seg["start"], seg["end"]):
                    xs.append(-(cy + x_shift) - (d/2 if d else 0.0))
                    ys.append(self.distance_from_bottom + cx)

        if not xs:
            self._draw_labels(painter, None)
            return

        # extra margin on the right so CG/CP symbols don't clip
        MARGIN     = 55
        SYM_ROOM   = 38   # reserved pixels on right for symbols
        LABEL_ROOM = 55   # reserved pixels at bottom for text

        avail_w = self.width()  - 2*MARGIN - SYM_ROOM
        avail_h = self.height() - 2*MARGIN - LABEL_ROOM

        w_world = (max(xs) - min(xs)) or 1.0
        h_world = (max(ys) - min(ys)) or 1.0

        scale    = min(avail_w / w_world, avail_h / h_world)
        world_cx = (min(xs) + max(xs)) / 2
        world_cy = (min(ys) + max(ys)) / 2
        scr_cx   = (self.width() - SYM_ROOM) / 2
        scr_cy   = (self.height() - LABEL_ROOM) / 2

        def to_s(wx, wy):
            """World → screen.  Y axis is flipped (world up = screen up)."""
            return (
                (wx - world_cx) * scale + scr_cx,
                -(wy - world_cy) * scale + scr_cy
            )

        # ---- body (rectangle) ------------------------------------------------
        if L and d:
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            x1, y1 = to_s(-d/2, 0)
            x2, y2 = to_s( d/2, L)
            painter.drawRect(
                int(min(x1,x2)), int(min(y1,y2)),
                int(abs(x2-x1)), int(abs(y2-y1))
            )

        # ---- fins (canonical lines) ------------------------------------------
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        body_half = (d/2) if d else 0.0
        for i in range(self.fin_count):
            x_shift = i * (self.fin_span + gap)
            for seg in self.fin_canonical:
                cx1, cy1 = seg["start"]
                cx2, cy2 = seg["end"]
                wx1 = -(cy1 + x_shift) - body_half
                wy1 = self.distance_from_bottom + cx1
                wx2 = -(cy2 + x_shift) - body_half
                wy2 = self.distance_from_bottom + cx2
                sx1, sy1 = to_s(wx1, wy1)
                sx2, sy2 = to_s(wx2, wy2)
                painter.drawLine(int(sx1), int(sy1), int(sx2), int(sy2))

        # ---- CG / CP symbols -------------------------------------------------
        sym_r = 11
        body_rx, _ = to_s(body_half, 0)    # right edge of body, screen-x

        if self.cg_from_nose is not None and L:
            _, sy = to_s(0, L - self.cg_from_nose)
            sym_x = int(body_rx) + sym_r + 5
            painter.setPen(QPen(CG_BORDER, 1))
            painter.drawLine(int(body_rx), int(sy), sym_x - sym_r, int(sy))
            self._draw_cg(painter, sym_x, int(sy), sym_r)

        if self.cp_from_nose is not None and L:
            _, sy = to_s(0, L - self.cp_from_nose)
            sym_x = int(body_rx) + sym_r + 5
            painter.setPen(QPen(CP_BORDER, 1))
            painter.drawLine(int(body_rx), int(sy), sym_x - sym_r, int(sy))
            self._draw_cp(painter, sym_x, int(sy), sym_r)

        # ---- labels ----------------------------------------------------------
        self._draw_labels(painter, L)


    # ------------------------------------------------------------------ symbols

    def _draw_cg(self, painter, cx, cy, r):
        """Crash-test-dummy style: two opposite quadrants filled yellow."""
        rect = (cx-r, cy-r, 2*r, 2*r)
        # white background
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(*rect)
        # two quadrants filled yellow
        painter.setBrush(QBrush(CG_FILL))
        painter.drawPie(*rect,   0*16, 90*16)   # top-right
        painter.drawPie(*rect, 180*16, 90*16)   # bottom-left
        # border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(CG_BORDER, 1.5))
        painter.drawEllipse(*rect)
        # cross lines
        painter.drawLine(cx-r, cy, cx+r, cy)
        painter.drawLine(cx,  cy-r, cx,  cy+r)

    def _draw_cp(self, painter, cx, cy, r):
        """Dot inside a circle, blue."""
        rect = (cx-r, cy-r, 2*r, 2*r)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(CP_FILL, 2))
        painter.drawEllipse(*rect)
        dot = max(3, r // 3)
        painter.setBrush(QBrush(CP_FILL))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx-dot, cy-dot, 2*dot, 2*dot)


    # ------------------------------------------------------------------ labels

    def _draw_labels(self, painter, body_length):
        unit   = "mm"   if self.unit_mm else "cm"
        toggle = "cm"   if self.unit_mm else "mm"
        factor = 1.0    if self.unit_mm else 0.1   # 1 DXF unit = 1 mm assumed

        entries = []
        if self.cg_from_nose is not None:
            entries.append((f"CG: {self.cg_from_nose*factor:.1f} {unit}", CG_BORDER))
        if self.cp_from_nose is not None:
            entries.append((f"CP: {self.cp_from_nose*factor:.1f} {unit}", CP_BORDER))

        painter.setFont(QFont("Arial", 9))
        fm = painter.fontMetrics()
        lh = fm.height() + 2

        if not entries:
            note = f"CG/CP: enter dimensions  [{unit} — click to switch]"
            painter.setPen(QColor(180, 180, 180))
            x = self.width()  - fm.horizontalAdvance(note) - 6
            y = self.height() - 8
            painter.drawText(x, y, note)
            self._lbl_rect = QRect(x-2, y-fm.height(), fm.horizontalAdvance(note)+4, lh)
            return

        toggle_txt = f"[click to switch to {toggle}]"
        all_txts   = [e[0] for e in entries] + [toggle_txt]
        max_w  = max(fm.horizontalAdvance(t) for t in all_txts)
        total_h = lh * len(all_txts) + 4

        x0 = self.width()  - max_w - 10
        y0 = self.height() - total_h - 8

        # semi-transparent background
        painter.setBrush(QBrush(QColor(255, 255, 255, 210)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x0-4, y0-2, max_w+8, total_h+4)

        y = y0 + fm.ascent()
        for txt, color in entries:
            painter.setPen(QPen(color, 1))
            painter.drawText(x0, y, txt)
            y += lh

        painter.setPen(QColor(120, 120, 120))
        painter.drawText(x0, y, toggle_txt)

        self._lbl_rect = QRect(x0-4, y0-2, max_w+8, total_h+4)
