import * as THREE from 'three';

function cylinderBetween(a, b, radius, material) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const mesh = new THREE.Mesh(
    new THREE.CylinderGeometry(radius, radius * 0.86, len, 10),
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

function makeLeg(points, material) {
  const g = new THREE.Group();
  for (let i = 0; i < points.length - 1; i++) {
    g.add(cylinderBetween(points[i], points[i + 1], 0.025, material));
  }
  return g;
}

export function createFly() {
  const root = new THREE.Group();
  root.rotation.y = -0.55;

  const shell = new THREE.MeshStandardMaterial({
    color: 0x292d28,
    roughness: 0.42,
    metalness: 0.08,
  });

  const abdomenMat = new THREE.MeshStandardMaterial({
    color: 0x2d3427,
    roughness: 0.5,
  });

  const stripeMat = new THREE.MeshStandardMaterial({
    color: 0x6b7040,
    roughness: 0.48,
  });

  const eyeMat = new THREE.MeshStandardMaterial({
    color: 0xa8202f,
    roughness: 0.36,
    emissive: 0x2b0208,
    emissiveIntensity: 0.25,
  });

  const wingMat = new THREE.MeshPhysicalMaterial({
    color: 0xe8f2f0,
    transparent: true,
    opacity: 0.34,
    roughness: 0.12,
    transmission: 0.18,
    side: THREE.DoubleSide,
    depthWrite: false,
  });

  const legMat = new THREE.MeshStandardMaterial({
    color: 0x171a17,
    roughness: 0.58,
  });

  // Coordinate convention:
  // +X = face/front, -X = abdomen.
  const thorax = new THREE.Mesh(new THREE.SphereGeometry(0.34, 32, 24), shell);
  thorax.scale.set(1.08, 0.92, 0.88);
  thorax.castShadow = true;
  root.add(thorax);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.23, 32, 24), shell);
  head.position.set(0.48, 0.01, 0);
  head.scale.set(0.95, 0.9, 0.98);
  head.castShadow = true;
  root.add(head);

  for (const z of [-0.17, 0.17]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.13, 26, 18), eyeMat);
    eye.position.set(0.59, 0.045, z);
    eye.scale.set(0.72, 1.02, 0.92);
    eye.castShadow = true;
    root.add(eye);
  }

  const abdomen = new THREE.Mesh(new THREE.SphereGeometry(0.42, 34, 24), abdomenMat);
  abdomen.position.set(-0.53, -0.01, 0);
  abdomen.scale.set(1.35, 0.78, 0.78);
  abdomen.castShadow = true;
  root.add(abdomen);

  // Abdomen bands.
  for (const x of [-0.32, -0.52, -0.72]) {
    const band = new THREE.Mesh(
      new THREE.TorusGeometry(0.255, 0.028, 12, 42),
      stripeMat
    );
    band.position.set(x, -0.01, 0);
    band.rotation.y = Math.PI / 2;
    band.scale.set(1, 0.82, 0.82);
    root.add(band);
  }

  // Antennae.
  for (const z of [-0.10, 0.10]) {
    root.add(makeLeg([
      new THREE.Vector3(0.63, 0.12, z),
      new THREE.Vector3(0.82, 0.25, z * 1.4),
      new THREE.Vector3(0.97, 0.31, z * 1.65),
    ], legMat));
  }

  // Proboscis.
  const proboscis = cylinderBetween(
    new THREE.Vector3(0.66, -0.10, 0),
    new THREE.Vector3(0.88, -0.18, 0),
    0.035,
    legMat
  );
  root.add(proboscis);

  // Wings are true geometry, not sprites.
  const wingGeo = new THREE.ShapeGeometry((() => {
    const s = new THREE.Shape();
    s.moveTo(0, 0);
    s.bezierCurveTo(0.35, 0.06, 0.82, 0.12, 1.16, 0.05);
    s.bezierCurveTo(1.32, -0.02, 1.08, -0.27, 0.68, -0.32);
    s.bezierCurveTo(0.34, -0.35, 0.08, -0.18, 0, 0);
    return s;
  })());

  const leftWingPivot = new THREE.Group();
  leftWingPivot.position.set(-0.08, 0.24, -0.16);
  leftWingPivot.rotation.set(-0.35, 0.05, -0.18);
  root.add(leftWingPivot);

  const leftWing = new THREE.Mesh(wingGeo, wingMat);
  leftWing.rotation.x = Math.PI / 2;
  leftWing.scale.set(0.95, 0.95, 0.95);
  leftWingPivot.add(leftWing);

  const rightWingPivot = new THREE.Group();
  rightWingPivot.position.set(-0.08, 0.24, 0.16);
  rightWingPivot.rotation.set(0.35, -0.05, 0.18);
  root.add(rightWingPivot);

  const rightWing = new THREE.Mesh(wingGeo, wingMat);
  rightWing.rotation.x = -Math.PI / 2;
  rightWing.scale.set(0.95, 0.95, 0.95);
  rightWingPivot.add(rightWing);

  // Six articulated legs.
  const legSets = [
    // front
    [
      new THREE.Vector3(0.22, -0.18, -0.20),
      new THREE.Vector3(0.48, -0.40, -0.34),
      new THREE.Vector3(0.76, -0.55, -0.39),
    ],
    [
      new THREE.Vector3(0.22, -0.18, 0.20),
      new THREE.Vector3(0.48, -0.40, 0.34),
      new THREE.Vector3(0.76, -0.55, 0.39),
    ],
    // middle
    [
      new THREE.Vector3(-0.08, -0.20, -0.23),
      new THREE.Vector3(-0.02, -0.47, -0.48),
      new THREE.Vector3(0.16, -0.58, -0.68),
    ],
    [
      new THREE.Vector3(-0.08, -0.20, 0.23),
      new THREE.Vector3(-0.02, -0.47, 0.48),
      new THREE.Vector3(0.16, -0.58, 0.68),
    ],
    // rear
    [
      new THREE.Vector3(-0.32, -0.18, -0.20),
      new THREE.Vector3(-0.60, -0.40, -0.36),
      new THREE.Vector3(-0.78, -0.56, -0.55),
    ],
    [
      new THREE.Vector3(-0.32, -0.18, 0.20),
      new THREE.Vector3(-0.60, -0.40, 0.36),
      new THREE.Vector3(-0.78, -0.56, 0.55),
    ],
  ];

  const legs = legSets.map((points) => makeLeg(points, legMat));
  legs.forEach((leg) => root.add(leg));

  // Smoking foreleg rig.
  const smokingArm = new THREE.Group();
  smokingArm.position.set(0.24, -0.15, -0.20);
  root.add(smokingArm);

  const upper = cylinderBetween(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0.24, 0.16, -0.08),
    0.027,
    legMat
  );
  const lower = cylinderBetween(
    new THREE.Vector3(0.24, 0.16, -0.08),
    new THREE.Vector3(0.48, 0.20, -0.04),
    0.024,
    legMat
  );
  smokingArm.add(upper, lower);

  const cigarette = new THREE.Group();
  cigarette.position.set(0.73, 0.04, -0.24);
  cigarette.rotation.z = Math.PI / 2;
  root.add(cigarette);

  const paper = new THREE.Mesh(
    new THREE.CylinderGeometry(0.032, 0.032, 0.44, 18),
    new THREE.MeshStandardMaterial({ color: 0xf1e8d0, roughness: 0.72 })
  );
  paper.castShadow = true;
  cigarette.add(paper);

  const filter = new THREE.Mesh(
    new THREE.CylinderGeometry(0.033, 0.033, 0.11, 18),
    new THREE.MeshStandardMaterial({ color: 0xc98545, roughness: 0.65 })
  );
  filter.position.y = -0.165;
  cigarette.add(filter);

  const emberMat = new THREE.MeshStandardMaterial({
    color: 0xff6f3c,
    emissive: 0xff2500,
    emissiveIntensity: 2.8,
  });
  const ember = new THREE.Mesh(new THREE.CylinderGeometry(0.033, 0.033, 0.03, 18), emberMat);
  ember.position.y = 0.235;
  cigarette.add(ember);

  // Smoke particle puffs.
  const smoke = new THREE.Group();
  root.add(smoke);
  const smokeMat = new THREE.MeshBasicMaterial({
    color: 0xd9d6d2,
    transparent: true,
    opacity: 0,
    depthWrite: false,
  });
  const puffs = [];
  for (let i = 0; i < 9; i++) {
    const puff = new THREE.Mesh(
      new THREE.SphereGeometry(0.045 + i * 0.006, 14, 10),
      smokeMat.clone()
    );
    puff.position.set(0.78 + i * 0.025, 0.18 + i * 0.09, -0.24);
    smoke.add(puff);
    puffs.push(puff);
  }

  root.traverse((obj) => {
    if (obj.isMesh) obj.castShadow = true;
  });

  const state = {
    smokingUntil: 0,
    startedAt: 0,
  };

  function triggerSmoke(duration = 1.8) {
    const now = performance.now() / 1000;
    state.startedAt = now;
    state.smokingUntil = now + duration;
  }

  function update(t) {
    // Tiny living motions.
    root.position.y = Math.sin(t * 2.2) * 0.012;
    root.rotation.z = Math.sin(t * 1.1) * 0.015;

    leftWingPivot.rotation.z = -0.18 + Math.sin(t * 5.2) * 0.018;
    rightWingPivot.rotation.z = 0.18 - Math.sin(t * 5.2) * 0.018;

    const smoking = t < state.smokingUntil;
    if (smoking) {
      const local = t - state.startedAt;
      const inhale = Math.sin(Math.min(1, local / 0.75) * Math.PI * 0.5);
      smokingArm.rotation.z = -0.45 * inhale;
      smokingArm.rotation.y = -0.15 * inhale;
      cigarette.position.x = THREE.MathUtils.lerp(0.73, 0.49, inhale);
      cigarette.position.y = THREE.MathUtils.lerp(0.04, -0.02, inhale);
      emberMat.emissiveIntensity = 2.8 + inhale * 5.5;

      puffs.forEach((puff, i) => {
        const start = 0.45 + i * 0.08;
        const a = THREE.MathUtils.clamp((local - start) / 0.7, 0, 1);
        puff.material.opacity = Math.sin(a * Math.PI) * 0.34;
        puff.position.y = 0.18 + i * 0.09 + a * 0.30;
        puff.position.x = 0.78 + i * 0.025 + Math.sin(t * 1.7 + i) * 0.045;
        puff.scale.setScalar(1 + a * 1.2);
      });
    } else {
      smokingArm.rotation.z *= 0.86;
      smokingArm.rotation.y *= 0.86;
      cigarette.position.x = THREE.MathUtils.lerp(cigarette.position.x, 0.73, 0.12);
      cigarette.position.y = THREE.MathUtils.lerp(cigarette.position.y, 0.04, 0.12);
      emberMat.emissiveIntensity = THREE.MathUtils.lerp(
        emberMat.emissiveIntensity,
        2.8,
        0.1
      );
      puffs.forEach((puff, i) => {
        puff.material.opacity *= 0.82;
        puff.position.set(0.78 + i * 0.025, 0.18 + i * 0.09, -0.24);
        puff.scale.setScalar(1);
      });
    }
  }

  return { group: root, update, triggerSmoke };
}
