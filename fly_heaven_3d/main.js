import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createFly } from './fly_model.js';

const app = document.querySelector('#app');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe18f73);

const camera = new THREE.PerspectiveCamera(
  47,
  window.innerWidth / window.innerHeight,
  0.1,
  100
);
camera.position.set(0, 3.05, 8.2);
camera.lookAt(0, 1.85, -2.2);

// Render deliberately a little chunky so the 3D world keeps the
// original DOOMFLY / pixel-cartoon character.
const renderer = new THREE.WebGLRenderer({ antialias: false });
renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.BasicShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;
app.appendChild(renderer.domElement);

function sizeRenderer() {
  const scale = 0.72;
  const w = Math.max(480, Math.floor(window.innerWidth * scale));
  const h = Math.max(270, Math.floor(window.innerHeight * scale));
  renderer.setSize(w, h, false);
}
sizeRenderer();

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 1.75, -2.1);
controls.minDistance = 5.8;
controls.maxDistance = 12;
controls.maxPolarAngle = Math.PI * 0.48;

// ------------------------------------------------------------
// Flat cartoon lighting
// ------------------------------------------------------------

scene.add(new THREE.HemisphereLight(0xffc7a8, 0x49372d, 2.25));

const sunLight = new THREE.DirectionalLight(0xffad73, 2.8);
sunLight.position.set(5, 8, 3);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(1024, 1024);
sunLight.shadow.camera.left = -8;
sunLight.shadow.camera.right = 8;
sunLight.shadow.camera.top = 8;
sunLight.shadow.camera.bottom = -8;
scene.add(sunLight);

function mat(color) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: 0.92,
    metalness: 0,
    flatShading: true,
  });
}

function box(w, h, d, material, x, y, z) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

// ------------------------------------------------------------
// The same simple room as the old FLY HEAVEN, now actual 3D.
// ------------------------------------------------------------

const floorMat = mat(0x865b32);
const seamMat = mat(0x3f2c22);
const wallMat = mat(0xd77c70);
const sideWallMat = mat(0xc96f67);
const frameMat = mat(0x36383a);

box(12.5, 0.22, 12.5, floorMat, 0, -0.08, 0);
box(12.5, 7.0, 0.24, wallMat, 0, 3.35, -6.0);
box(0.24, 7.0, 12.5, sideWallMat, -6.15, 3.35, 0);
box(0.24, 7.0, 12.5, sideWallMat, 6.15, 3.35, 0);

// Floor planks like the screenshot.
for (let z = -5.7; z <= 5.8; z += 0.72) {
  box(12.1, 0.018, 0.035, seamMat, 0, 0.045, z);
}

// A few long seams give stronger perspective.
for (let x = -5.5; x <= 5.5; x += 1.5) {
  box(0.025, 0.019, 11.8, seamMat, x, 0.047, 0);
}

// ------------------------------------------------------------
// Window: two panes, striped sunset, mountains, sun.
// Every element is 3D geometry sitting just in front of the wall.
// ------------------------------------------------------------

const windowRoot = new THREE.Group();
windowRoot.position.set(0, 3.75, -5.84);
scene.add(windowRoot);

const windowW = 8.35;
const windowH = 4.1;

// Sunset horizontal bands.
const bandColors = [
  0x515254,
  0x5d5c5a,
  0x876f62,
  0xb95559,
  0xc85d61,
  0xd26d6c,
  0xde8577,
  0xe99a70,
];

for (let i = 0; i < bandColors.length; i++) {
  const h = windowH / bandColors.length;
  const band = new THREE.Mesh(
    new THREE.PlaneGeometry(windowW - 0.28, h + 0.025),
    new THREE.MeshBasicMaterial({ color: bandColors[i] })
  );
  band.position.set(0, windowH / 2 - h / 2 - i * h, 0);
  windowRoot.add(band);
}

// Mountain silhouette.
function mountainShape(points, xOffset = 0) {
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0] + xOffset, points[0][1]);
  for (let i = 1; i < points.length; i++) {
    shape.lineTo(points[i][0] + xOffset, points[i][1]);
  }
  const mesh = new THREE.Mesh(
    new THREE.ShapeGeometry(shape),
    new THREE.MeshBasicMaterial({ color: 0x3b3d3f, side: THREE.DoubleSide })
  );
  mesh.position.set(0, -1.85, 0.03);
  windowRoot.add(mesh);
}

mountainShape([
  [-4.0, 0],
  [-4.0, 0.62],
  [-3.18, 1.05],
  [-2.20, 0.42],
  [-1.20, 1.34],
  [-0.02, 0.22],
  [0.3, 0],
]);

mountainShape([
  [-0.3, 0],
  [0.0, 0.42],
  [1.25, 0.95],
  [2.08, 0.32],
  [3.02, 0.82],
  [4.0, 0.42],
  [4.0, 0],
]);

const sun = new THREE.Mesh(
  new THREE.CircleGeometry(0.58, 24),
  new THREE.MeshBasicMaterial({ color: 0xffc596 })
);
sun.position.set(2.15, 0.28, 0.05);
windowRoot.add(sun);

// Thick frame, deliberately blocky.
function framePart(w, h, x, y) {
  const f = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.18), frameMat);
  f.position.set(x, y, 0.15);
  f.castShadow = true;
  windowRoot.add(f);
}

framePart(windowW + 0.35, 0.25, 0, windowH / 2 + 0.12);
framePart(windowW + 0.35, 0.25, 0, -windowH / 2 - 0.12);
framePart(0.25, windowH + 0.50, -windowW / 2 - 0.12, 0);
framePart(0.25, windowH + 0.50, windowW / 2 + 0.12, 0);
framePart(0.20, windowH + 0.20, 0, 0);

// ------------------------------------------------------------
// Cartoon 3D fly, in the same lower-center composition.
// ------------------------------------------------------------

const fly = createFly();
fly.group.position.set(0.05, 0.78, 1.05);
fly.group.scale.setScalar(1.18);
fly.group.rotation.y = -0.18;
scene.add(fly.group);

// ------------------------------------------------------------
// Live neural bridge
// ------------------------------------------------------------
//
// run_heaven.py writes real MN9-driven SMOKE events to
// /tmp/fly_heaven.log. bridge.mjs tails that log and exposes only
// NEW runtime events over Server-Sent Events.
//
// Neural event -> browser event -> this exact 3D animation.
const bridge = new EventSource('http://127.0.0.1:8787/events');

bridge.addEventListener('smoke', (event) => {
  const data = JSON.parse(event.data);
  console.log(
    `MN9 → SMOKE #${data.count} | song ${data.songSeconds.toFixed(2)}s | ${data.phase}`
  );
  fly.triggerSmoke();
});

bridge.addEventListener('reward', () => {
  console.log('PAM07 reward');
});

bridge.addEventListener('training_complete', () => {
  console.log('training complete — weights frozen');
});

bridge.addEventListener('open', () => {
  console.log('FLY HEAVEN neural bridge connected');
});

bridge.addEventListener('error', () => {
  console.log('waiting for FLY HEAVEN neural bridge...');
});

// Keep S as an explicit visual-only test key.
window.addEventListener('keydown', (event) => {
  if (event.key.toLowerCase() === 's') {
    fly.triggerSmoke();
  }
});

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  fly.update(clock.getElapsedTime());
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  sizeRenderer();
});
