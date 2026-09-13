import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { rotate4, project4To3, v4 } from './math4d.js';
import { createFly4DParts } from './fly4d.js';

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
renderer.toneMappingExposure = 1.35;
app.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 0, 0);
controls.minDistance = 5;
controls.maxDistance = 20;

scene.add(new THREE.HemisphereLight(0xb9a9ff, 0x130d1e, 1.7));

const keyLight = new THREE.PointLight(0xff87c8, 42, 25, 2);
keyLight.position.set(4, 5, 7);
scene.add(keyLight);

const fillLight = new THREE.PointLight(0x71caff, 34, 25, 2);
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
const tessColors = new Float32Array(tesseractEdges.length * 2 * 3);

tesseractGeometry.setAttribute(
  'position',
  new THREE.BufferAttribute(tessPositions, 3)
);
tesseractGeometry.setAttribute(
  'color',
  new THREE.BufferAttribute(tessColors, 3)
);

const tesseractMaterial = new THREE.LineBasicMaterial({
  vertexColors: true,
  transparent: true,
  opacity: 0.70,
});

const tesseractLines = new THREE.LineSegments(
  tesseractGeometry,
  tesseractMaterial
);
scene.add(tesseractLines);

const tessPointGeometry = new THREE.BufferGeometry();
const tessPointPositions = new Float32Array(tesseractVertices4.length * 3);
const tessPointColors = new Float32Array(tesseractVertices4.length * 3);

tessPointGeometry.setAttribute(
  'position',
  new THREE.BufferAttribute(tessPointPositions, 3)
);
tessPointGeometry.setAttribute(
  'color',
  new THREE.BufferAttribute(tessPointColors, 3)
);

const tessPoints = new THREE.Points(
  tessPointGeometry,
  new THREE.PointsMaterial({
    vertexColors: true,
    size: 0.082,
    sizeAttenuation: true,
  })
);
scene.add(tessPoints);

// ------------------------------------------------------------
// Readable 4D fly
// ------------------------------------------------------------

const flyParts = createFly4DParts();

const flyPalette = {
  body: 0x41444b,
  head: 0x30333a,
  abdomen: 0x6b6844,
  butt: 0x514f3d,
  eye: 0xff314b,
  wing: 0xdce6ff,
  leg: 0x1b1b24,
};

// ------------------------------------------------------------
// Make the invisible fourth coordinate visible as color.
//
// negative W -> cyan
// W ~= 0    -> pale violet
// positive W -> hot magenta
//
// We blend that signal with each anatomical base color so the fly
// remains readable while its hidden 4D position becomes visible.
// ------------------------------------------------------------

const wNegative = new THREE.Color(0x35d9ff);
const wZero = new THREE.Color(0xd9ccff);
const wPositive = new THREE.Color(0xff4fa7);

function colorFromW(w, baseHex, out = new THREE.Color()) {
  // tanh keeps extreme perspective excursions from blowing out the scale.
  const n = Math.tanh(w / 1.15); // roughly -1 .. +1
  const wColor = new THREE.Color();

  if (n < 0) {
    wColor.lerpColors(wZero, wNegative, -n);
  } else {
    wColor.lerpColors(wZero, wPositive, n);
  }

  const base = new THREE.Color(baseHex);

  // Keep some anatomy-specific color, but make W unmistakable.
  out.copy(base).lerp(wColor, 0.68);
  return out;
}

const flyViews = flyParts.map((part) => {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(part.points.length * 3);
  const colors = new Float32Array(part.points.length * 3);

  geometry.setAttribute(
    'position',
    new THREE.BufferAttribute(positions, 3)
  );
  geometry.setAttribute(
    'color',
    new THREE.BufferAttribute(colors, 3)
  );

  if (part.type === 'surface') {
    geometry.setIndex(part.indices);

    const transparent = part.kind === 'wing';

    const material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      vertexColors: true,
      roughness: 0.72,
      metalness: 0.02,
      side: THREE.DoubleSide,
      transparent,
      opacity: transparent ? 0.42 : 0.94,
      depthWrite: !transparent,
      flatShading: false,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.renderOrder = transparent ? 3 : 1;
    scene.add(mesh);

    // Dynamic wire overlay makes the 4D deformation legible.
    const wireMaterial = new THREE.MeshBasicMaterial({
      color:
        part.kind === 'eye' ? 0xff8a99 :
        part.kind === 'wing' ? 0xbdd0ff :
        0xa8a1c3,
      wireframe: true,
      transparent: true,
      opacity:
        part.kind === 'wing' ? 0.30 :
        part.kind === 'eye' ? 0.20 :
        0.11,
      depthWrite: false,
    });

    const wire = new THREE.Mesh(geometry, wireMaterial);
    wire.renderOrder = 4;
    scene.add(wire);

    return {
      part,
      geometry,
      positions,
      colors,
      objects: [mesh, wire],
    };
  }

  const lineMaterial = new THREE.LineBasicMaterial({
    vertexColors: true,
    transparent: true,
    opacity: 0.98,
  });

  const line = new THREE.Line(geometry, lineMaterial);
  scene.add(line);

  return {
    part,
    geometry,
    positions,
    colors,
    objects: [line],
  };
});

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
    xy: 0.10 * Math.sin(t * 0.17),
    yz: 0.08 * Math.sin(t * 0.21),

    xw: enabled.xw ? t * 0.32 : 0,
    yw: enabled.yw ? t * 0.20 : 0,
    zw: enabled.zw ? t * 0.14 : 0,
  };
}

function updateTesseract(angles) {
  const rotated = tesseractVertices4.map((p) => {
    const scaled = {
      x: p.x * 2.35,
      y: p.y * 2.35,
      z: p.z * 2.35,
      w: p.w * 2.35,
    };

    return rotate4(scaled, angles);
  });

  const projected = rotated.map((q) => project4To3(q, 7.0));

  const tmpColor = new THREE.Color();
  let k = 0;

  for (const [a, b] of tesseractEdges) {
    tessPositions[k] = projected[a].x;
    tessPositions[k + 1] = projected[a].y;
    tessPositions[k + 2] = projected[a].z;

    colorFromW(rotated[a].w, 0xb893ff, tmpColor);
    tessColors[k] = tmpColor.r;
    tessColors[k + 1] = tmpColor.g;
    tessColors[k + 2] = tmpColor.b;
    k += 3;

    tessPositions[k] = projected[b].x;
    tessPositions[k + 1] = projected[b].y;
    tessPositions[k + 2] = projected[b].z;

    colorFromW(rotated[b].w, 0xb893ff, tmpColor);
    tessColors[k] = tmpColor.r;
    tessColors[k + 1] = tmpColor.g;
    tessColors[k + 2] = tmpColor.b;
    k += 3;
  }

  tesseractGeometry.attributes.position.needsUpdate = true;
  tesseractGeometry.attributes.color.needsUpdate = true;

  for (let i = 0; i < projected.length; i++) {
    const p3 = projected[i];
    const q4 = rotated[i];

    tessPointPositions[i * 3 + 0] = p3.x;
    tessPointPositions[i * 3 + 1] = p3.y;
    tessPointPositions[i * 3 + 2] = p3.z;

    colorFromW(q4.w, 0xf2d9ff, tmpColor);
    tessPointColors[i * 3 + 0] = tmpColor.r;
    tessPointColors[i * 3 + 1] = tmpColor.g;
    tessPointColors[i * 3 + 2] = tmpColor.b;
  }

  tessPointGeometry.attributes.position.needsUpdate = true;
  tessPointGeometry.attributes.color.needsUpdate = true;
}

function updateFly(angles) {
  // Independent offsets make the fly occupy R^4 instead of being a
  // rigid decorative object pasted into the tesseract.
  const flyAngles = {
    ...angles,
    xw: angles.xw + 0.29,
    yw: angles.yw - 0.13,
    zw: angles.zw + 0.09,
  };

  const tmpColor = new THREE.Color();

  for (const view of flyViews) {
    for (let i = 0; i < view.part.points.length; i++) {
      const q = rotate4(view.part.points[i], flyAngles);
      const p = project4To3(q, 6.0);

      view.positions[i * 3 + 0] = p.x;
      view.positions[i * 3 + 1] = p.y;
      view.positions[i * 3 + 2] = p.z;

      colorFromW(
        q.w,
        flyPalette[view.part.kind],
        tmpColor
      );

      view.colors[i * 3 + 0] = tmpColor.r;
      view.colors[i * 3 + 1] = tmpColor.g;
      view.colors[i * 3 + 2] = tmpColor.b;
    }

    view.geometry.attributes.position.needsUpdate = true;
    view.geometry.attributes.color.needsUpdate = true;

    if (view.part.type === 'surface') {
      view.geometry.computeVertexNormals();
    }
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
