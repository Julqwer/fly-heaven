import { v4, add4, scale4 } from './math4d.js';

function sampleHyperEllipsoid(center, radii, count, seedPhase = 0) {
  const pts = [];

  // Deterministic quasi-random sampling on S^3.
  for (let i = 0; i < count; i++) {
    const a = (i * 2.399963229728653 + seedPhase) % (Math.PI * 2);
    const b = ((i + 0.5) / count) * Math.PI;
    const c = (i * 1.61803398875 + seedPhase * 0.7) % (Math.PI * 2);

    const s = Math.sin(b);
    const q = v4(
      Math.cos(a) * s,
      Math.sin(a) * s,
      Math.cos(b) * Math.cos(c),
      Math.cos(b) * Math.sin(c)
    );

    pts.push(v4(
      center.x + q.x * radii.x,
      center.y + q.y * radii.y,
      center.z + q.z * radii.z,
      center.w + q.w * radii.w
    ));
  }

  return pts;
}

function polyline4(points, samplesPerSegment = 4) {
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

export function createFly4DPoints() {
  const parts = [];

  // The body is not a 3D mesh with an extra number attached.
  // Each volume below is sampled in four dimensions (x,y,z,w).
  parts.push({
    name: 'thorax',
    kind: 'body',
    points: sampleHyperEllipsoid(
      v4(0.0, 0.0, 0.0, 0.0),
      v4(0.72, 0.55, 0.52, 0.42),
      120,
      0.1
    ),
  });

  parts.push({
    name: 'head',
    kind: 'head',
    points: sampleHyperEllipsoid(
      v4(-0.88, 0.05, 0.0, -0.12),
      v4(0.46, 0.42, 0.42, 0.34),
      80,
      0.7
    ),
  });

  parts.push({
    name: 'abdomen',
    kind: 'abdomen',
    points: sampleHyperEllipsoid(
      v4(1.05, -0.03, 0.0, 0.18),
      v4(0.92, 0.52, 0.52, 0.48),
      145,
      1.3
    ),
  });

  for (const side of [-1, 1]) {
    parts.push({
      name: side < 0 ? 'eye-left' : 'eye-right',
      kind: 'eye',
      points: sampleHyperEllipsoid(
        v4(-1.11, 0.09, side * 0.31, -0.16),
        v4(0.22, 0.25, 0.16, 0.13),
        38,
        side < 0 ? 2.0 : 2.7
      ),
    });
  }

  // Wings have noticeable extension into W, so 4D rotation visibly
  // changes their apparent topology after projection.
  for (const side of [-1, 1]) {
    parts.push({
      name: side < 0 ? 'wing-left' : 'wing-right',
      kind: 'wing',
      points: sampleHyperEllipsoid(
        v4(0.34, 0.63, side * 0.42, side * 0.32),
        v4(1.0, 0.18, 0.34, 0.56),
        92,
        side < 0 ? 3.1 : 3.8
      ),
    });
  }

  const legRoots = [
    [-0.34, -0.32, -0.32, -0.05],
    [-0.34, -0.32,  0.32,  0.05],
    [ 0.05, -0.36, -0.38, -0.08],
    [ 0.05, -0.36,  0.38,  0.08],
    [ 0.52, -0.30, -0.30, -0.12],
    [ 0.52, -0.30,  0.30,  0.12],
  ];

  legRoots.forEach((r, i) => {
    const side = Math.sign(r[2]) || 1;

    parts.push({
      name: `leg-${i + 1}`,
      kind: 'leg',
      points: polyline4([
        v4(...r),
        v4(r[0] + 0.18, -0.74, r[2] + side * 0.28, r[3] + side * 0.18),
        v4(r[0] + 0.46, -1.00, r[2] + side * 0.50, r[3] + side * 0.36),
      ], 7),
    });
  });

  // Antennae.
  for (const side of [-1, 1]) {
    parts.push({
      name: side < 0 ? 'antenna-left' : 'antenna-right',
      kind: 'leg',
      points: polyline4([
        v4(-1.16, 0.25, side * 0.11, -0.18),
        v4(-1.43, 0.58, side * 0.18, -0.04),
        v4(-1.62, 0.72, side * 0.23, 0.18),
      ], 6),
    });
  }

  return parts;
}
