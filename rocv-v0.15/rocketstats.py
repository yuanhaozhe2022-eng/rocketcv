import math


class RocketStats:

    def __init__(self, rocket):
        self.rocket = rocket
        self.mass = None
        self.cg = None        # distance from nose (top of body)
        self.cp = None        # distance from nose
        self.stability = None # in calibers (positive = stable)


    def compute(self, wall_str, density_str, fin_thickness_str):
        """
        Compute CG and CP.  Both are measured from the nose (top of rocket).
        Requires body.length and body.diameter to be set.
        """
        self.cg = None
        self.cp = None
        self.stability = None
        self.mass = None

        body = self.rocket.body
        fin  = self.rocket.fin

        if body is None or body.length is None or body.diameter is None:
            return

        L = body.length
        d = body.diameter

        def _flt(s):
            try:
                v = float(s)
                return v if v > 0 else None
            except (ValueError, TypeError):
                return None

        wall   = _flt(wall_str)
        rho    = _flt(density_str)
        t_fin  = _flt(fin_thickness_str) or wall   # fall back to body wall

        # ---- CP  (Barrowman, fins only — no nose cone geometry available) ----
        if fin is not None and all(v is not None for v in [
                fin.root_chord, fin.tip_chord, fin.height, fin.sweep_length]):

            Cr  = fin.root_chord
            Ct  = fin.tip_chord
            s   = fin.height        # span
            Lf  = fin.sweep_length  # leading-edge sweep (positive = backward)
            dfb = fin.distance_from_bottom or 0

            denom = Cr + Ct
            if denom > 0 and s > 0:
                # Barrowman CP from root leading edge, along body axis
                X_f = (Lf * (Cr + 2*Ct)) / (3*denom) + \
                      (Cr**2 + Cr*Ct + Ct**2) / (6*denom)
                # root leading edge is Cr above root_back, root_back is dfb above tail
                # → root LE is (L - dfb - Cr) from nose
                x_root_le = L - dfb - Cr
                self.cp = x_root_le + X_f

        # ---- CG (mass-weighted centroid) ----
        masses   = []
        moments  = []   # mass × distance from nose

        # Body tube (thin-wall hollow cylinder)
        if wall is not None and rho is not None:
            m_body = math.pi * d * wall * L * rho
            masses.append(m_body)
            moments.append(m_body * L / 2.0)

        # Fins
        if (fin is not None and fin.area is not None
                and t_fin is not None and rho is not None):
            m_fins = fin.count * fin.area * t_fin * rho
            cg_fin = self._fin_cg_from_nose(fin, L)
            if cg_fin is not None:
                masses.append(m_fins)
                moments.append(m_fins * cg_fin)

        if masses and sum(masses) > 0:
            self.mass = sum(masses)
            self.cg   = sum(moments) / self.mass

        # ---- Stability ----
        if self.cg is not None and self.cp is not None and d > 0:
            self.stability = (self.cp - self.cg) / d


    def _fin_centroid_chordwise(self, fin):
        """Centroid distance along chordwise axis from root_back (0 = root_back)."""
        Cr = fin.root_chord
        Ct = fin.tip_chord
        s  = fin.height
        Lf = fin.sweep_length
        if any(v is None for v in [Cr, Ct, s, Lf]):
            return Cr / 2.0 if Cr else None
        # Canonical trapezoid vertices (chordwise, spanwise):
        # (0,0), (Cr,0), (Cr-Lf, s), (Cr-Lf-Ct, s)
        pts = [(0,0), (Cr,0), (Cr-Lf, s), (Cr-Lf-Ct, s)]
        A  = 0.0
        cx = 0.0
        n  = len(pts)
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[(i+1) % n]
            cross = xi*yj - xj*yi
            A  += cross
            cx += (xi+xj) * cross
        A /= 2.0
        if abs(A) < 1e-9:
            return Cr / 2.0
        return cx / (6.0 * A)


    def _fin_cg_from_nose(self, fin, body_length):
        cg_chord = self._fin_centroid_chordwise(fin)
        if cg_chord is None:
            return None
        # root_back is at (body_length - dfb) from nose;
        # moving cg_chord units toward root_front = moving toward nose
        return (body_length - fin.distance_from_bottom) - cg_chord
