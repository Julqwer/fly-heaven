import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createFly } from './fly_model.js';

const app = document.querySelector('#app');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1b1422);
scene.fog = new THREE.FogExp2(0x2a1722, 0.018);

const camera = new THREE.PerspectiveCamera(
  48,
  window.innerWidth / window.innerHeight,
  0.1,
  200
);
camera.position.set(10, 7, 13);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(1.25, 2.55, -1.0);
controls.minDistance = 3.0;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.49;

// ------------------------------------------------------------
// Lighting
// ------------------------------------------------------------

scene.add(new THREE.HemisphereLight(0xffd6b2, 0x241c31, 1.5));

const sunset = new THREE.DirectionalLight(0xff9366, 4.0);
sunset.position.set(-7, 8, -8);
sunset.castShadow = true;
sunset.shadow.mapSize.set(2048, 2048);
sunset.shadow.camera.left = -14;
sunset.shadow.camera.right = 14;
sunset.shadow.camera.top = 14;
sunset.shadow.camera.bottom = -14;
scene.add(sunset);

const fill = new THREE.PointLight(0xe2b8ff, 20, 24, 2);
fill.position.set(6, 5, 7);
scene.add(fill);

const flyKey = new THREE.PointLight(0xffc49f, 8, 5, 2);
flyKey.position.set(2.4, 4.0, 1.2);
scene.add(flyKey);

// ------------------------------------------------------------
// Materials
// ------------------------------------------------------------

const floorMat = new THREE.MeshStandardMaterial({
  color: 0x4e332f,
  roughness: 0.78,
  metalness: 0.03,
});

const wallMat = new THREE.MeshStandardMaterial({
  color: 0x8e5f5f,
  roughness: 0.88,
});

const darkWallMat = new THREE.MeshStandardMaterial({
  color: 0x4f3d4f,
  roughness: 0.95,
});

const trimMat = new THREE.MeshStandardMaterial({
  color: 0x2d252d,
  roughness: 0.7,
});

// ------------------------------------------------------------
// Room
// ------------------------------------------------------------

function box(w, h, d, material, x, y, z) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    material
  );
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

box(18, 0.28, 14, floorMat, 0, 0, 0);
box(18, 8.2, 0.28, wallMat, 0, 4, -7);
box(0.28, 8.2, 14, darkWallMat, -9, 4, 0);

for (let z = -6.6; z < 7; z += 0.72) {
  box(17.7, 0.012, 0.025, trimMat, 0, 0.15, z);
}

// ------------------------------------------------------------
// Window + sunset
// ------------------------------------------------------------

const windowGroup = new THREE.Group();
windowGroup.position.set(-3.6, 4.1, -6.82);
scene.add(windowGroup);

const frameMat = new THREE.MeshStandardMaterial({
  color: 0x241d25,
  roughness: 0.6,
});

const glassMat = new THREE.MeshBasicMaterial({
  color: 0xfd9a7d,
  transparent: true,
  opacity: 0.38,
  side: THREE.DoubleSide,
});

const glass = new THREE.Mesh(
  new THREE.PlaneGeometry(6.4, 4.2),
  glassMat
);
glass.position.z = 0.05;
windowGroup.add(glass);

const frameParts = [
  [6.7, 0.18, 0.15, 0, 2.18, 0],
  [6.7, 0.18, 0.15, 0, -2.18, 0],
  [0.18, 4.55, 0.15, -3.34, 0, 0],
  [0.18, 4.55, 0.15, 3.34, 0, 0],
  [0.12, 4.25, 0.12, 0, 0, 0.06],
];

for (const [w, h, d, x, y, z] of frameParts) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), frameMat);
  m.position.set(x, y, z);
  windowGroup.add(m);
}

const sunDisc = new THREE.Mesh(
  new THREE.CircleGeometry(1.15, 64),
  new THREE.MeshBasicMaterial({ color: 0xffd4a3 })
);
sunDisc.position.set(-5.4, 4.8, -7.3);
scene.add(sunDisc);

const horizon = new THREE.Mesh(
  new THREE.PlaneGeometry(17, 8),
  new THREE.ShaderMaterial({
    depthWrite: false,
    side: THREE.DoubleSide,
    uniforms: {
      cTop: { value: new THREE.Color(0x74456f) },
      cMid: { value: new THREE.Color(0xe46d72) },
      cBottom: { value: new THREE.Color(0xffc58b) },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 cTop;
      uniform vec3 cMid;
      uniform vec3 cBottom;
      varying vec2 vUv;
      void main() {
        vec3 col;
        if (vUv.y > 0.45) {
          float t = (vUv.y - 0.45) / 0.55;
          col = mix(cMid, cTop, t);
        } else {
          float t = vUv.y / 0.45;
          col = mix(cBottom, cMid, t);
        }
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  })
);
horizon.position.set(-4.0, 4.0, -7.42);
scene.add(horizon);

// ------------------------------------------------------------
// Furniture
// ------------------------------------------------------------

const tableMat = new THREE.MeshStandardMaterial({
  color: 0x56332c,
  roughness: 0.64,
});

box(5.2, 0.28, 2.4, tableMat, 1.6, 2.0, -1.1);
box(0.28, 2.0, 0.28, tableMat, -0.5, 1.0, -2.0);
box(0.28, 2.0, 0.28, tableMat, 3.7, 1.0, -2.0);
box(0.28, 2.0, 0.28, tableMat, -0.5, 1.0, -0.2);
box(0.28, 2.0, 0.28, tableMat, 3.7, 1.0, -0.2);

// ------------------------------------------------------------
// TRUE 3D fly
// ------------------------------------------------------------

const fly = createFly();
fly.group.position.set(1.35, 2.63, -1.02);
fly.group.scale.setScalar(0.92);
scene.add(fly.group);

// Press S only as a local animation preview.
// Later this exact trigger will be wired to MN9 runtime events.
window.addEventListener('keydown', (event) => {
  if (event.key.toLowerCase() === 's') {
    fly.triggerSmoke();
  }
});

// dust motes
const particleCount = 220;
const positions = new Float32Array(particleCount * 3);
for (let i = 0; i < particleCount; i++) {
  positions[i * 3 + 0] = THREE.MathUtils.randFloatSpread(16);
  positions[i * 3 + 1] = THREE.MathUtils.randFloat(0.2, 7.4);
  positions[i * 3 + 2] = THREE.MathUtils.randFloat(-6.2, 6.2);
}

const dustGeo = new THREE.BufferGeometry();
dustGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

const dust = new THREE.Points(
  dustGeo,
  new THREE.PointsMaterial({
    color: 0xffd9bc,
    size: 0.025,
    transparent: true,
    opacity: 0.35,
    depthWrite: false,
  })
);
scene.add(dust);

// ------------------------------------------------------------
// Render loop
// ------------------------------------------------------------

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const t = clock.getElapsedTime();
  controls.update();
  fly.update(t);

  dust.rotation.y = t * 0.006;

  renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
