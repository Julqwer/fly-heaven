import * as THREE from 'three';

export function v4(x, y, z, w) {
  return { x, y, z, w };
}

export function add4(a, b) {
  return v4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w);
}

export function scale4(a, s) {
  return v4(a.x * s, a.y * s, a.z * s, a.w * s);
}

function rotatePair(a, b, angle) {
  const c = Math.cos(angle);
  const s = Math.sin(angle);
  return [a * c - b * s, a * s + b * c];
}

export function rotate4(p, angles) {
  let { x, y, z, w } = p;

  if (angles.xy) [x, y] = rotatePair(x, y, angles.xy);
  if (angles.xz) [x, z] = rotatePair(x, z, angles.xz);
  if (angles.yz) [y, z] = rotatePair(y, z, angles.yz);

  // Rotations that actually mix the hidden fourth coordinate into
  // visible coordinates. These are what make the projection morph.
  if (angles.xw) [x, w] = rotatePair(x, w, angles.xw);
  if (angles.yw) [y, w] = rotatePair(y, w, angles.yw);
  if (angles.zw) [z, w] = rotatePair(z, w, angles.zw);

  return v4(x, y, z, w);
}

export function project4To3(p, distance = 4.8) {
  const denom = Math.max(0.35, distance - p.w);
  const k = distance / denom;

  return new THREE.Vector3(
    p.x * k,
    p.y * k,
    p.z * k
  );
}
