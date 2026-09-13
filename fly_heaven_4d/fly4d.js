import { v4 } from './math4d.js';

function shell4D(center, radii, latSegments = 12, lonSegments = 20, wWarp = 0.35, phase = 0) {
  const points = [];
  const indices = [];

  for (let iy = 0; iy <= latSegments; iy++) {
    const theta = (iy / latSegments) * Math.PI;
    const st = Math.sin(theta);
    const ct = Math.cos(theta);

    for (let ix = 0; ix <= lonSegments; ix++) {
      const phi = (ix / lonSegments) * Math.PI * 2;
      const cp = Math.cos(phi);
      const sp = Math.sin(phi);

      // A closed 2D shell embedded in R^4.
      // x/y/z make the familiar body surface, while w bends that
      // surface through the hidden fourth coordinate.
      const sx = st * cp;
      const sy = ct;
      const sz = st * sp;
      const sw =
        st *
        (0.62 * Math.sin(2 * phi + phase) +
         0.38 * Math.sin(3 * theta - phase));

      points.push(v4(
        center.x + radii.x * sx,
        center.y + radii.y * sy,
        center.z + radii.z * sz,
        center.w + radii.w * wWarp * sw
      ));
    }
  }

  const row = lonSegments + 1;

  for (let iy = 0; iy < latSegments; iy++) {
    for (let ix = 0; ix < lonSegments; ix++) {
      const a = iy * row + ix;
      const b = a + row;
      const c = b + 1;
      const d = a + 1;

      indices.push(a, b, d);
      indices.push(b, c, d);
    }
  }

  return { points, indices };
}

function wing4D(center, side, rows = 8, cols = 18) {
  const points = [];
  const indices = [];

  for (let iy = 0; iy <= rows; iy++) {
    const v = iy / rows;
    const span = Math.sin(v * Math.PI);

    for (let ix = 0; ix <= cols; ix++) {
      const u = ix / cols;
      const x = (u - 0.10) * 1.55;
      const y = (v - 0.5) * 0.56 * span;
      const z = side * (0.18 + u * 0.30 + 0.06 * Math.sin(v * Math.PI));
      const w = side * (0.18 + 0.48 * Math.sin(u * Math.PI) * span);

      points.push(v4(
        center.x + x,
        center.y + y,
        center.z + z,
        center.w + w
      ));
    }
  }

  const row = cols + 1;

  for (let iy = 0; iy < rows; iy++) {
    for (let ix = 0; ix < cols; ix++) {
      const a = iy * row + ix;
      const b = a + row;
      const c = b + 1;
      const d = a + 1;

      indices.push(a, b, d);
      indices.push(b, c, d);
    }
  }

  return { points, indices };
}

function polyline4(points, samplesPerSegment = 5) {
  const out = [];

  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i];
    const b = points[i + 1];

    for (let j = 0; j < samplesPerSegment; j++) {
      const t = j / samplesPerSegment;
      out.push(v4(
        a.x + (b.x - a.x) * t,
        a.y + (b.y - a.y) * t,
        a.z + (b.z - a.z) * t,
        a.w + (b.w - a.w) * t
      ));
    }
  }

  out.push(points[points.length - 1]);
  return out;
}

function surfacePart(name, kind, shell) {
  return {
    name,
    kind,
    type: 'surface',
    points: shell.points,
    indices: shell.indices,
  };
}

function linePart(name, kind, points) {
  return {
    name,
    kind,
    type: 'line',
    points,
  };
}

export function createFly4DParts() {
  const parts = [];

  // Chunky cartoon body, but every surface vertex has x/y/z/w.
  parts.push(surfacePart(
    'thorax',
    'body',
    shell4D(
      v4(0.0, 0.0, 0.0, 0.00),
      v4(0.72, 0.55, 0.52, 0.52),
      13,
      22,
      0.95,
      0.2
    )
  ));

  parts.push(surfacePart(
    'head',
    'head',
    shell4D(
      v4(-0.90, 0.06, 0.0, -0.12),
      v4(0.48, 0.42, 0.42, 0.42),
      12,
      20,
      0.90,
      1.1
    )
  ));

  parts.push(surfacePart(
    'abdomen',
    'abdomen',
    shell4D(
      v4(1.06, -0.03, 0.0, 0.18),
      v4(0.96, 0.55, 0.54, 0.58),
      14,
      24,
      0.95,
      2.0
    )
  ));

  // Tiny cute 4D butt cheeks at the rear.
  for (const side of [-1, 1]) {
    parts.push(surfacePart(
      side < 0 ? 'butt-left' : 'butt-right',
      'butt',
      shell4D(
        v4(1.74, -0.10, side * 0.16, 0.22 + side * 0.08),
        v4(0.28, 0.27, 0.22, 0.26),
        9,
        14,
        0.85,
        side < 0 ? 0.7 : 2.4
      )
    ));
  }

  for (const side of [-1, 1]) {
    parts.push(surfacePart(
      side < 0 ? 'eye-left' : 'eye-right',
      'eye',
      shell4D(
        v4(-1.16, 0.10, side * 0.31, -0.17),
        v4(0.24, 0.26, 0.17, 0.18),
        9,
        14,
        0.85,
        side < 0 ? 0.4 : 2.7
      )
    ));
  }

  for (const side of [-1, 1]) {
    parts.push(surfacePart(
      side < 0 ? 'wing-left' : 'wing-right',
      'wing',
      wing4D(
        v4(-0.03, 0.46, 0.0, 0.0),
        side
      )
    ));
  }

  const legRoots = [
    [-0.36, -0.30, -0.30, -0.05],
    [-0.36, -0.30,  0.30,  0.05],
    [ 0.05, -0.36, -0.36, -0.08],
    [ 0.05, -0.36,  0.36,  0.08],
    [ 0.52, -0.30, -0.30, -0.12],
    [ 0.52, -0.30,  0.30,  0.12],
  ];

  legRoots.forEach((r, i) => {
    const side = Math.sign(r[2]) || 1;

    parts.push(linePart(
      `leg-${i + 1}`,
      'leg',
      polyline4([
        v4(...r),
        v4(r[0] + 0.12, -0.72, r[2] + side * 0.28, r[3] + side * 0.20),
        v4(r[0] + 0.40, -1.02, r[2] + side * 0.54, r[3] + side * 0.38),
      ], 6)
    ));
  });

  for (const side of [-1, 1]) {
    parts.push(linePart(
      side < 0 ? 'antenna-left' : 'antenna-right',
      'leg',
      polyline4([
        v4(-1.16, 0.25, side * 0.11, -0.18),
        v4(-1.43, 0.58, side * 0.18, -0.02),
        v4(-1.62, 0.72, side * 0.23, 0.20),
      ], 6)
    ));
  }

  return parts;
}
