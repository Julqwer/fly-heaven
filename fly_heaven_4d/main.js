import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { rotate4, project4To3, v4 } from './math4d.js';
import { createFly4DPoints } from './fly4d.js';

const app = document.querySelector('#app');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x09070f);
scene.fog = new THREE.FogExp2(0x09070f, 0.028);

const camera = new THREE.PerspectiveCamera(
  46,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(7.8, 5.3, 9.4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 0, 0);
controls.minDistance = 5;
controls.maxDistance = 20;

scene.add(new THREE.HemisphereLight(0xa99cff, 0x130d1e, 1.35));

const keyLight = new THREE.PointLight(0xff87c8, 28, 25, 2);
keyLight.position.set(4, 5, 7);
scene.add(keyLight);

const fillLight = new THREE.PointLight(0x71caff, 22, 25, 2);
fillLight.position.set(-6, -1, 3);
scene.add(fillLight);

// ------------------------------------------------------------
// Tesseract in R^4
// ------------------------------------------------------------

const tesseractVertices4 = [];
for (const x of [-1, 1]) {
  for (const y of [-1, 1]) {
    for (const z of [-1, 1]) {
      for (const w of [-1, 1]) {
        tesseractVertices4.push(v4(x, y, z, w));
      }
    }
  }
}

const tesseractEdges = [];
for (let i = 0; i < tesseractVertices4.length; i++) {
  for (let j = i + 1; j < tesseractVertices4.length; j++) {
    const a = tesseractVertices4[i];
    const b = tesseractVertices4[j];

    const diffs =
      Number(a.x !== b.x) +
      Number(a.y !== b.y) +
      Number(a.z !== b.z) +
      Number(a.w !== b.w);

    if (diffs === 1) {
      tesseractEdges.push([i, j]);
    }
  }
}

const tesseractGeometry = new THREE.BufferGeometry();
const tessPositions = new Float32Array(tesseractEdges.length * 2 * 3);
tesseractGeometry.setAttribute(
  'position',
  new THREE.BufferAttribute(tessPositions, 3)
);

const tesseractMaterial = new THREE.LineBasicMaterial({
  color: 0xb893ff,
  transparent: true,
  opacity: 0.78,
});

const tesseractLines = new THREE.LineSegments(
  tesseractGeometry,
  tesseractMaterial
);
scene.add(tesseractLines);

// Ghost vertices.
const tessPointGeometry = new THREE.BufferGeometry();
const tessPointPositions = new Float32Array(tesseractVertices4.length * 3);
tessPointGeometry.setAttribute(
  'position',
  new THREE.BufferAttribute(tessPointPositions, 3)
);

const tessPoints = new THREE.Points(
  tessPointGeometry,
  new THREE.PointsMaterial({
    color: 0xf2d9ff,
    size: 0.075,
    sizeAttenuation: true,
  })
);
scene.add(tessPoints);

// ------------------------------------------------------------
// 4D fly
// ------------------------------------------------------------

const flyParts = createFly4DPoints();

const flyPalette = {
  body: 0x4e5148,
  head: 0x34363a,
  abdomen: 0x6d6845,
  eye: 0xff4154,
  wing: 0xd9e2ff,
  leg: 0x25242d,
};

const partViews = flyParts.map((part) => {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(part.points.length * 3);

  geometry.setAttribute(
    'position',
    new THREE.BufferAttribute(positions, 3)
  );

  const material = new THREE.PointsMaterial({
    color: flyPalette[part.kind],
    size:
      part.kind === 'eye' ? 0.095 :
      part.kind === 'leg' ? 0.055 :
      part.kind === 'wing' ? 0.075 :
      0.085,
    transparent: part.kind === 'wing',
    opacity: part.kind === 'wing' ? 0.52 : 0.95,
    depthWrite: part.kind !== 'wing',
    sizeAttenuation: true,
  });

  const points = new THREE.Points(geometry, material);
  scene.add(points);

  return {
    part,
    geometry,
    positions,
  };
});

// A faint center marker so the viewer can tell that the fly itself,
// not the tesseract, is changing under 4D rotations.
const center = new THREE.Mesh(
  new THREE.SphereGeometry(0.055, 12, 8),
  new THREE.MeshBasicMaterial({ color: 0xffffff })
);
scene.add(center);

// ------------------------------------------------------------
// 4D animation controls
// ------------------------------------------------------------

let running = true;
const enabled = {
  xw: true,
  yw: true,
  zw: true,
};

window.addEventListener('keydown', (event) => {
  if (event.code === 'Space') {
    running = !running;
  }

  if (event.key === '1') enabled.xw = !enabled.xw;
  if (event.key === '2') enabled.yw = !enabled.yw;
  if (event.key === '3') enabled.zw = !enabled.zw;
});

const clock = new THREE.Clock();
let phase = 0;

function angles4(t) {
  return {
    xy: 0.17 * Math.sin(t * 0.19),
    yz: 0.11 * Math.sin(t * 0.23),

    xw: enabled.xw ? t * 0.37 : 0,
    yw: enabled.yw ? t * 0.23 : 0,
    zw: enabled.zw ? t * 0.17 : 0,
  };
}

function updateTesseract(angles) {
  const projected = tesseractVertices4.map((p) => {
    const scaled = {
      x: p.x * 2.35,
      y: p.y * 2.35,
      z: p.z * 2.35,
      w: p.w * 2.35,
    };

    return project4To3(
      rotate4(scaled, angles),
      7.0
    );
  });

  let k = 0;
  for (const [a, b] of tesseractEdges) {
    tessPositions[k++] = projected[a].x;
    tessPositions[k++] = projected[a].y;
    tessPositions[k++] = projected[a].z;

    tessPositions[k++] = projected[b].x;
    tessPositions[k++] = projected[b].y;
    tessPositions[k++] = projected[b].z;
  }

  tesseractGeometry.attributes.position.needsUpdate = true;

  for (let i = 0; i < projected.length; i++) {
    tessPointPositions[i * 3 + 0] = projected[i].x;
    tessPointPositions[i * 3 + 1] = projected[i].y;
    tessPointPositions[i * 3 + 2] = projected[i].z;
  }

  tessPointGeometry.attributes.position.needsUpdate = true;
}

function updateFly(angles) {
  // A little independent XW phase offset makes the fly genuinely
  // occupy the same R^4 habitat without being rigidly glued to the cage.
  const flyAngles = {
    ...angles,
    xw: angles.xw + 0.31,
    yw: angles.yw - 0.14,
  };

  for (const view of partViews) {
    const points = view.part.points;

    for (let i = 0; i < points.length; i++) {
      const q = rotate4(points[i], flyAngles);
      const p = project4To3(q, 5.5);

      view.positions[i * 3 + 0] = p.x;
      view.positions[i * 3 + 1] = p.y;
      view.positions[i * 3 + 2] = p.z;
    }

    view.geometry.attributes.position.needsUpdate = true;
  }
}

function animate() {
  requestAnimationFrame(animate);

  const dt = clock.getDelta();
  if (running) phase += dt;

  const angles = angles4(phase);

  updateTesseract(angles);
  updateFly(angles);

  controls.update();
  renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
