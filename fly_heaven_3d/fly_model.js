import * as THREE from 'three';

function flatMaterial(color, extra = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    roughness: 0.88,
    metalness: 0,
    flatShading: true,
    ...extra,
  });
}

function segment(a, b, radius, material, sides = 6) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radius, radius, dir.length(), sides),
    material
  );
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    dir.clone().normalize()
  );
  mesh.castShadow = true;
  return mesh;
}

function limb(points, material, radius = 0.022) {
  const group = new THREE.Group();
  for (let i = 0; i < points.length - 1; i++) {
    group.add(segment(points[i], points[i + 1], radius, material));
  }
  return group;
}

export function createFly() {
  const root = new THREE.Group();

  // Cartoon palette matching the original 2D sprite.
  const bodyMat = flatMaterial(0x313236);
  const abdomenMat = flatMaterial(0x3c3d33);
  const stripeMat = flatMaterial(0x6b6540);
  const eyeMat = flatMaterial(0xd92739, {
    emissive: 0x350006,
    emissiveIntensity: 0.3,
  });
  const legMat = flatMaterial(0x1c2022);
  const wingMat = new THREE.MeshStandardMaterial({
    color: 0xd8d5cf,
    roughness: 0.95,
    transparent: true,
    opacity: 0.48,
    side: THREE.DoubleSide,
    depthWrite: false,
    flatShading: true,
  });

  // Body: intentionally chunky and cute, not anatomically photorealistic.
  const thorax = new THREE.Mesh(
    new THREE.SphereGeometry(0.38, 12, 8),
    bodyMat
  );
  thorax.scale.set(1.05, 0.95, 0.95);
  thorax.castShadow = true;
  root.add(thorax);

  const abdomen = new THREE.Mesh(
    new THREE.SphereGeometry(0.43, 12, 8),
    abdomenMat
  );
  abdomen.position.set(0.58, -0.02, 0);
  abdomen.scale.set(1.25, 0.88, 0.88);
  abdomen.castShadow = true;
  root.add(abdomen);

  // Wide olive bands like the old fly.
  for (const x of [0.38, 0.62, 0.83]) {
    const band = new THREE.Mesh(
      new THREE.TorusGeometry(0.305, 0.038, 6, 18),
      stripeMat
    );
    band.position.set(x, -0.02, 0);
    band.rotation.y = Math.PI / 2;
    band.scale.set(1, 0.86, 0.86);
    root.add(band);
  }

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.28, 12, 8),
    bodyMat
  );
  head.position.set(-0.47, 0.03, 0);
  head.scale.set(0.95, 0.92, 0.98);
  head.castShadow = true;
  root.add(head);

  // Comically large red eyes, the signature of the 2D version.
  for (const z of [-0.16, 0.16]) {
    const eye = new THREE.Mesh(
      new THREE.SphereGeometry(0.15, 10, 7),
      eyeMat
    );
    eye.position.set(-0.60, 0.055, z);
    eye.scale.set(0.95, 1.08, 0.92);
    eye.castShadow = true;
    root.add(eye);
  }

  // Antennae.
  for (const z of [-0.095, 0.095]) {
    root.add(limb([
      new THREE.Vector3(-0.63, 0.16, z),
      new THREE.Vector3(-0.78, 0.34, z * 1.45),
      new THREE.Vector3(-0.88, 0.40, z * 1.6),
    ], legMat, 0.014));
  }

  // Short proboscis.
  root.add(segment(
    new THREE.Vector3(-0.66, -0.10, 0),
    new THREE.Vector3(-0.82, -0.16, 0),
    0.032,
    legMat
  ));

  // Big rounded translucent wings.
  function wing(side) {
    const pivot = new THREE.Group();
    pivot.position.set(0.02, 0.25, side * 0.18);

    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.48, 12, 8),
      wingMat
    );
    mesh.scale.set(1.25, 0.58, 0.10);
    mesh.position.set(0.12, 0.34, side * 0.12);
    mesh.rotation.z = side * 0.08;
    mesh.castShadow = false;
    pivot.add(mesh);
    root.add(pivot);
    return pivot;
  }

  const leftWing = wing(-1);
  const rightWing = wing(1);

  // Six stick-like legs, deliberately simple like the sprite.
  const legs = [
    [
      new THREE.Vector3(-0.20, -0.20, -0.18),
      new THREE.Vector3(-0.38, -0.46, -0.34),
      new THREE.Vector3(-0.55, -0.58, -0.46),
    ],
    [
      new THREE.Vector3(-0.20, -0.20, 0.18),
      new THREE.Vector3(-0.38, -0.46, 0.34),
      new THREE.Vector3(-0.55, -0.58, 0.46),
    ],
    [
      new THREE.Vector3(0.04, -0.22, -0.22),
      new THREE.Vector3(0.06, -0.50, -0.44),
      new THREE.Vector3(-0.05, -0.62, -0.62),
    ],
    [
      new THREE.Vector3(0.04, -0.22, 0.22),
      new THREE.Vector3(0.06, -0.50, 0.44),
      new THREE.Vector3(-0.05, -0.62, 0.62),
    ],
    [
      new THREE.Vector3(0.34, -0.19, -0.18),
      new THREE.Vector3(0.58, -0.43, -0.34),
      new THREE.Vector3(0.72, -0.58, -0.50),
    ],
    [
      new THREE.Vector3(0.34, -0.19, 0.18),
      new THREE.Vector3(0.58, -0.43, 0.34),
      new THREE.Vector3(0.72, -0.58, 0.50),
    ],
  ];
  legs.forEach((points) => root.add(limb(points, legMat)));

  // Smoking foreleg + cigarette.
  const smokingArm = new THREE.Group();
  smokingArm.position.set(-0.20, -0.18, -0.18);
  smokingArm.add(limb([
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(-0.16, 0.14, -0.08),
    new THREE.Vector3(-0.38, 0.15, -0.09),
  ], legMat));
  root.add(smokingArm);

  const cigarette = new THREE.Group();
  cigarette.position.set(-0.88, -0.01, -0.19);
  cigarette.rotation.z = Math.PI / 2;
  root.add(cigarette);

  const paper = new THREE.Mesh(
    new THREE.CylinderGeometry(0.028, 0.028, 0.42, 8),
    flatMaterial(0xf2ead8)
  );
  cigarette.add(paper);

  const filter = new THREE.Mesh(
    new THREE.CylinderGeometry(0.029, 0.029, 0.10, 8),
    flatMaterial(0xc57b38)
  );
  filter.position.y = 0.16;
  cigarette.add(filter);

  const emberMat = flatMaterial(0xff6334, {
    emissive: 0xff2f00,
    emissiveIntensity: 2.0,
  });
  const ember = new THREE.Mesh(
    new THREE.CylinderGeometry(0.029, 0.029, 0.035, 8),
    emberMat
  );
  ember.position.y = -0.225;
  cigarette.add(ember);

  // Puffy cartoon smoke.
  const puffs = [];
  for (let i = 0; i < 8; i++) {
    const puff = new THREE.Mesh(
      new THREE.SphereGeometry(0.055 + i * 0.008, 8, 6),
      new THREE.MeshBasicMaterial({
        color: 0xd7d0c9,
        transparent: true,
        opacity: 0,
        depthWrite: false,
      })
    );
    puff.position.set(-0.95 - i * 0.035, 0.12 + i * 0.10, -0.19);
    root.add(puff);
    puffs.push(puff);
  }

  root.traverse((obj) => {
    if (obj.isMesh && obj.material !== wingMat) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  const state = {
    smokeStart: -10,
    smokeUntil: -10,
    baseY: null,
  };

  function triggerSmoke(duration = 1.8) {
    const now = performance.now() / 1000;
    state.smokeStart = now;
    state.smokeUntil = now + duration;
  }

  function update(t) {
    // Keep the world placement from main.js. The old version accidentally
    // overwrote root.position.y every frame and sank the fly into the floor.
    if (state.baseY === null) state.baseY = root.position.y;
    root.position.y = state.baseY + Math.sin(t * 2.0) * 0.010;
    root.rotation.z = Math.sin(t * 1.2) * 0.012;

    leftWing.rotation.z = -0.03 + Math.sin(t * 4.8) * 0.018;
    rightWing.rotation.z = 0.03 - Math.sin(t * 4.8) * 0.018;

    const smoking = t < state.smokeUntil;
    if (smoking) {
      const local = t - state.smokeStart;
      const bring = THREE.MathUtils.smoothstep(
        THREE.MathUtils.clamp(local / 0.55, 0, 1),
        0,
        1
      );

      smokingArm.rotation.z = 0.62 * bring;
      smokingArm.rotation.y = -0.15 * bring;
      cigarette.position.x = THREE.MathUtils.lerp(-0.88, -0.70, bring);
      cigarette.position.y = THREE.MathUtils.lerp(-0.01, -0.08, bring);
      emberMat.emissiveIntensity = 2.0 + bring * 5.0;

      puffs.forEach((puff, i) => {
        const start = 0.38 + i * 0.07;
        const a = THREE.MathUtils.clamp((local - start) / 0.72, 0, 1);
        puff.material.opacity = Math.sin(a * Math.PI) * 0.38;
        puff.position.y = 0.12 + i * 0.10 + a * 0.28;
        puff.position.x = -0.95 - i * 0.035 - a * 0.06;
        puff.position.z = -0.19 + Math.sin(t * 1.7 + i) * 0.035;
        puff.scale.setScalar(1 + a * 0.9);
      });
    } else {
      smokingArm.rotation.z *= 0.84;
      smokingArm.rotation.y *= 0.84;
      cigarette.position.x = THREE.MathUtils.lerp(cigarette.position.x, -0.88, 0.12);
      cigarette.position.y = THREE.MathUtils.lerp(cigarette.position.y, -0.01, 0.12);
      emberMat.emissiveIntensity = THREE.MathUtils.lerp(
        emberMat.emissiveIntensity,
        2.0,
        0.12
      );
      puffs.forEach((puff, i) => {
        puff.material.opacity *= 0.80;
        puff.position.set(-0.95 - i * 0.035, 0.12 + i * 0.10, -0.19);
        puff.scale.setScalar(1);
      });
    }
  }

  return { group: root, update, triggerSmoke };
}
