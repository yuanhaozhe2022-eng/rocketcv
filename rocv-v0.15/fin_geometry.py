import math





def _x(p):
    return p.x if hasattr(p, "x") else p[0]


def _y(p):
    return p.y if hasattr(p, "y") else p[1]



def trace_loops(lines):

    if not lines:
        return []

    segments = []
    xs = []
    ys = []

    for line in lines:
        sx, sy = _x(line["start"]), _y(line["start"])
        ex, ey = _x(line["end"]), _y(line["end"])
        segments.append(((sx, sy), (ex, ey)))
        xs.extend([sx, ex])
        ys.extend([sy, ey])

    if not xs:
        return []

    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    tol = span * 1e-6

    def key(p):
        return (round(p[0] / tol), round(p[1] / tol))

    adjacency = {}

    for idx, (a, b) in enumerate(segments):
        ka, kb = key(a), key(b)
        adjacency.setdefault(ka, []).append((idx, b, kb))
        adjacency.setdefault(kb, []).append((idx, a, ka))

    used = [False] * len(segments)
    loops = []

    for start_idx in range(len(segments)):

        if used[start_idx]:
            continue

        a, b = segments[start_idx]
        used[start_idx] = True

        path = [a, b]
        start_key = key(a)
        current_key = key(b)

        safety = len(segments) + 1

        while current_key != start_key and safety > 0:

            safety -= 1
            next_choice = None

            for seg_idx, other_pt, other_key in adjacency.get(current_key, []):
                if not used[seg_idx]:
                    next_choice = (seg_idx, other_pt, other_key)
                    break

            if next_choice is None:
                break

            seg_idx, other_pt, other_key = next_choice
            used[seg_idx] = True
            path.append(other_pt)
            current_key = other_key

        if current_key == start_key and len(path) >= 4:
            loops.append(path[:-1])  # drop the duplicate closing point

    return loops


def shoelace(points):

    n = len(points)
    area = 0.0

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2.0



def _perp_distance(point, line_start, line_end):

    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.hypot(x0 - x1, y0 - y1)

    t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    return math.hypot(x0 - proj_x, y0 - proj_y)


def _rdp_open(points, epsilon):

    if len(points) < 3:
        return points[:]

    start, end = points[0], points[-1]

    max_dist = -1.0
    max_idx = -1

    for i in range(1, len(points) - 1):
        d = _perp_distance(points[i], start, end)
        if d > max_dist:
            max_dist = d
            max_idx = i

    if max_dist <= epsilon:
        return [start, end]

    left = _rdp_open(points[:max_idx + 1], epsilon)
    right = _rdp_open(points[max_idx:], epsilon)

    return left[:-1] + right


def rdp_closed(points, epsilon):

    if len(points) < 4:
        return points[:]

    p0 = points[0]

    far_idx = max(
        range(1, len(points)),
        key=lambda i: (points[i][0] - p0[0]) ** 2 + (points[i][1] - p0[1]) ** 2
    )

    chain1 = points[:far_idx + 1]
    chain2 = points[far_idx:] + [p0]

    simplified1 = _rdp_open(chain1, epsilon)
    simplified2 = _rdp_open(chain2, epsilon)

    return simplified1[:-1] + simplified2[:-1]


def find_dominant_corners(loop_points, target=4):

    if len(loop_points) <= target:
        return loop_points[:]

    xs = [p[0] for p in loop_points]
    ys = [p[1] for p in loop_points]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0

    steps = 200
    lo_eps = span * 1e-4
    hi_eps = span * 0.5
    ratio = hi_eps / lo_eps

    candidates = []

    for i in range(steps + 1):
        frac = i / steps
        epsilon = lo_eps * (ratio ** frac)
        simplified = rdp_closed(loop_points, epsilon)
        candidates.append(simplified)

    exact = [c for c in candidates if len(c) == target]

    if exact:
        return exact[len(exact) // 2]  # middle of the stable plateau

    best = min(candidates, key=lambda c: (abs(len(c) - target), -len(c)))

    return best



def _loop_segments(loop_points):

    n = len(loop_points)
    segments = []

    for i in range(n):
        a = loop_points[i]
        b = loop_points[(i + 1) % n]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        segments.append({"a": a, "b": b, "length": length, "angle": angle})

    return segments


def _otsu_threshold(values):

    sorted_vals = sorted(values)
    n = len(sorted_vals)

    total_sum = sum(sorted_vals)

    best_thresh = None
    best_variance = -1.0

    sum_a = 0.0
    count_a = 0

    for i in range(n - 1):

        sum_a += sorted_vals[i]
        count_a += 1
        count_b = n - count_a

        if sorted_vals[i] == sorted_vals[i + 1]:
            continue  # don't split between equal values

        mean_a = sum_a / count_a
        mean_b = (total_sum - sum_a) / count_b

        between_var = count_a * count_b * (mean_a - mean_b) ** 2

        if between_var > best_variance:
            best_variance = between_var
            best_thresh = (sorted_vals[i] + sorted_vals[i + 1]) / 2

    return best_thresh


def _find_long_segment_indices(segments):

    n = len(segments)
    lengths = [s["length"] for s in segments]

    if n <= 8:
        return set(range(n))

    log_lengths = [math.log(max(l, 1e-9)) for l in lengths]
    threshold = _otsu_threshold(log_lengths)

    if threshold is None:
        order = sorted(range(n), key=lambda i: -lengths[i])
        return set(order[:4])

    long_indices = {i for i in range(n) if log_lengths[i] > threshold}

    if len(long_indices) < 3 or len(long_indices) > 16:
        order = sorted(range(n), key=lambda i: -lengths[i])
        return set(order[:4])

    return long_indices


def _angle_diff(a1, a2):
    d = abs(a1 - a2) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def _group_long_runs(segments, long_indices, angle_tol_deg=20.0):

    n = len(segments)
    is_long = [i in long_indices for i in range(n)]

    if all(is_long):
        return [list(range(n))]

    start = 0
    for i in range(n):
        if is_long[i] and not is_long[(i - 1) % n]:
            start = i
            break

    order = [(start + k) % n for k in range(n)]
    angle_tol = math.radians(angle_tol_deg)

    runs = []
    current = []
    prev_angle = None

    for idx in order:
        if is_long[idx]:
            seg_angle = segments[idx]["angle"]
            if current and prev_angle is not None and _angle_diff(seg_angle, prev_angle) > angle_tol:
                runs.append(current)
                current = []
            current.append(idx)
            prev_angle = seg_angle
        else:
            if current:
                runs.append(current)
                current = []
            prev_angle = None

    if current:
        runs.append(current)

    return runs


def _fit_line(points):

    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n

    sxx = sum((p[0] - cx) ** 2 for p in points)
    syy = sum((p[1] - cy) ** 2 for p in points)
    sxy = sum((p[0] - cx) * (p[1] - cy) for p in points)

    theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
    direction = (math.cos(theta), math.sin(theta))

    return (cx, cy), direction


def _line_intersection(p1, d1, p2, d2):

    x1, y1 = p1
    dx1, dy1 = d1
    x2, y2 = p2
    dx2, dy2 = d2

    denom = dx1 * dy2 - dy1 * dx2

    if abs(denom) < 1e-12:
        return None

    t = ((x2 - x1) * dy2 - (y2 - y1) * dx2) / denom

    return (x1 + t * dx1, y1 + t * dy1)


def find_corners_by_edge_fitting(loop_points):

    if len(loop_points) < 3:
        return None

    segments = _loop_segments(loop_points)
    long_indices = _find_long_segment_indices(segments)
    runs = _group_long_runs(segments, long_indices)

    if len(runs) not in (3, 4):
        return None

    lines = []

    for run in runs:
        pts = [segments[i]["a"] for i in run] + [segments[run[-1]]["b"]]
        point, direction = _fit_line(pts)

        if len(pts) > 2:
            residuals = [_perp_distance(p, point, (point[0] + direction[0], point[1] + direction[1])) for p in pts]
            median_res = sorted(residuals)[len(residuals) // 2]
            cutoff = max(median_res * 4, 1e-6)
            clean_pts = [p for p, r in zip(pts, residuals) if r <= cutoff]
            if len(clean_pts) >= 2:
                point, direction = _fit_line(clean_pts)

        lines.append((point, direction))

    n = len(lines)
    corners = []

    for i in range(n):
        p1, d1 = lines[i]
        p2, d2 = lines[(i + 1) % n]
        corner = _line_intersection(p1, d1, p2, d2)
        if corner is None:
            return None
        corners.append(corner)

    return corners



def _edge_vector(corners, i):
    n = len(corners)
    a, b = corners[i], corners[(i + 1) % n]
    return (b[0] - a[0], b[1] - a[1])


def _vector_angle(v1, v2):
    len1 = math.hypot(*v1)
    len2 = math.hypot(*v2)
    if len1 < 1e-9 or len2 < 1e-9:
        return 90.0
    cos_a = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
    cos_a = max(-1.0, min(1.0, cos_a))
    return math.degrees(math.acos(cos_a))


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _dims_from_corners(root_back, root_front, tip_back, tip_front):

    root_vec = (root_front[0] - root_back[0], root_front[1] - root_back[1])
    root_len = math.hypot(*root_vec)

    if root_len == 0:
        return None

    root_dir = (root_vec[0] / root_len, root_vec[1] / root_len)
    height_dir = (-root_dir[1], root_dir[0])

    mid_root = ((root_front[0] + root_back[0]) / 2, (root_front[1] + root_back[1]) / 2)
    mid_tip = ((tip_front[0] + tip_back[0]) / 2, (tip_front[1] + tip_back[1]) / 2)
    to_tip = (mid_tip[0] - mid_root[0], mid_tip[1] - mid_root[1])

    if _dot(height_dir, to_tip) < 0:
        height_dir = (-height_dir[0], -height_dir[1])

    tip_chord = math.hypot(tip_front[0] - tip_back[0], tip_front[1] - tip_back[1])

    height_front = _dot((tip_front[0] - root_front[0], tip_front[1] - root_front[1]), height_dir)
    height_back = _dot((tip_back[0] - root_back[0], tip_back[1] - root_back[1]), height_dir)
    height = (height_front + height_back) / 2

    sweep_length = _dot((root_front[0] - tip_front[0], root_front[1] - tip_front[1]), root_dir)

    return {
        "root_back": root_back, "root_front": root_front,
        "tip_back": tip_back, "tip_front": tip_front,
        "root_dir": root_dir, "height_dir": height_dir,
        "root_chord": root_len, "tip_chord": tip_chord,
        "height": height, "sweep_length": sweep_length,
    }


def classify_fin_shape(corners):

    if len(corners) == 4:

        e = [_edge_vector(corners, i) for i in range(4)]
        angle_02 = _vector_angle(e[0], (-e[2][0], -e[2][1]))
        angle_13 = _vector_angle(e[1], (-e[3][0], -e[3][1]))

        if angle_02 <= angle_13:
            chord_x = (corners[0], corners[1])
            chord_y = (corners[2], corners[3])
            connectors = [(corners[0], corners[3]), (corners[1], corners[2])]
        else:
            chord_x = (corners[1], corners[2])
            chord_y = (corners[3], corners[0])
            connectors = [(corners[1], corners[0]), (corners[2], corners[3])]

        len_x = math.hypot(chord_x[1][0] - chord_x[0][0], chord_x[1][1] - chord_x[0][1])
        len_y = math.hypot(chord_y[1][0] - chord_y[0][0], chord_y[1][1] - chord_y[0][1])

        root_is_x = len_x >= len_y

        if root_is_x:
            side_pairs = [(c[0], c[1]) for c in connectors]
        else:
            side_pairs = [(c[1], c[0]) for c in connectors]

        root_back, tip_back = side_pairs[0]
        root_front, tip_front = side_pairs[1]

    elif len(corners) == 3:

        e = [_edge_vector(corners, i) for i in range(3)]
        lens = [math.hypot(*v) for v in e]
        root_idx = lens.index(max(lens))

        root_back = corners[root_idx]
        root_front = corners[(root_idx + 1) % 3]
        apex = corners[(root_idx + 2) % 3]
        tip_back = tip_front = apex

    else:
        return None

    dims = _dims_from_corners(root_back, root_front, tip_back, tip_front)

    if dims is None:
        return None

    if dims["sweep_length"] < 0:
        swapped = _dims_from_corners(root_front, root_back, tip_front, tip_back)
        if swapped is not None:
            dims = swapped

    root_back = dims["root_back"]
    root_dir = dims["root_dir"]
    height_dir = dims["height_dir"]

    def transform(p):
        rel = (p[0] - root_back[0], p[1] - root_back[1])
        return (_dot(rel, root_dir), _dot(rel, height_dir))

    return {
        "root_chord": dims["root_chord"],
        "tip_chord": dims["tip_chord"],
        "height": dims["height"],
        "sweep_length": dims["sweep_length"],
        "sweep_angle_deg": math.degrees(math.atan2(dims["sweep_length"], dims["height"])) if dims["height"] else None,
        "corners": {
            "root_front": dims["root_front"], "root_back": dims["root_back"],
            "tip_front": dims["tip_front"], "tip_back": dims["tip_back"],
        },
        "transform": transform,
    }



def extract_fin_dimensions(lines):

    loops = trace_loops(lines)

    if not loops:
        return None

    main_loop = max(loops, key=shoelace)

    if len(main_loop) < 3:
        return None

    corners = find_corners_by_edge_fitting(main_loop)
    result = classify_fin_shape(corners) if corners else None

    if result is not None:
        return result

    corners4 = find_dominant_corners(main_loop, target=4)
    result = classify_fin_shape(corners4) if len(corners4) == 4 else None

    if result is None:
        corners3 = find_dominant_corners(main_loop, target=3)
        result = classify_fin_shape(corners3) if len(corners3) == 3 else None

    return result