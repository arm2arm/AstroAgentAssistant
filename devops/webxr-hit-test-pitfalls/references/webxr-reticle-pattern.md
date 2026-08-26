# WebXR Reticle Implementation Pattern

## Context
This file documents the concrete implementation patterns discovered while fixing the AR door placement marker in `/home/hermes/projects/webxr-portal-door/`.

## Root Causes

### 1. Three.js r160+ Readonly Position Error
```javascript
// WRONG: Throws "cannot assign to readonly property 'position'"
reticle.matrix.decompose(pos, quat, scale);
```

In Three.js r160+, `Object3D.position` is a getter-only property. Calling `matrix.decompose()` on a Group tries to write back to `position`, causing an exception that aborts all setup.

**Fix:** Use `getWorldPosition()`/`getWorldQuaternion()` instead.

### 2. Hit-test Reference Space Mismatch
```javascript
// WRONG: hit-test requested with 'viewer' but pose extraction uses 'local-floor'
session.requestReferenceSpace('viewer');  // referenceSpace = viewer
session.requestHitTestSource({ space: viewerSpace });
// ... later ...
const pose = results[0].getPose(referenceSpace); // referenceSpace is local-floor → returns null
```

This caused `getPose()` to silently return `null`, so `reticle.visible = true` never executed.

**Fix:** Use the **SAME** reference space for both `requestHitTestSource()` and `frame.getHitTestResults()` pose extraction.

### 3. Reticle Rotation Destroyed by Matrix Overwrite
```javascript
// WRONG: reticle.matrix.fromArray(hitPose.transform.matrix) overwrites rotation
reticle.matrixAutoUpdate = false;  // breaks Three.js transform chain
reticle.rotation.x = -Math.PI / 2;  // faces ground
// ... every frame ...
reticle.matrix.fromArray(pose.transform.matrix);  // DESTROYS rotation → ring appears edge-on
```

The ring geometry requires `-PI/2` X rotation to lie flat on the ground. Overwriting the raw matrix each frame removes this rotation, rendering the ring invisible (edge-on to camera).

**Fix:** Use `reticle.matrixAutoUpdate = true` and set `reticle.position` from `pose.transform.position`.

### 4. Reticle Not Visible by Default
On many Android devices, hit-test never produces results (no ARCore support, no flat surface detected). The old pattern `reticle.visible = false` meant the marker would never appear.

**Fix:** Show reticle immediately at 2m in front of camera, then update to ground when hit-test succeeds.

## Correct Pattern (as implemented in webxr-portal-door)

```javascript
// 1. Build reticle as Group with visible=true
const reticleGroup = new THREE.Group();

const ringMesh = new THREE.Mesh(
    new THREE.RingGeometry(0.35, 0.55, 48),
    new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 1, side: THREE.DoubleSide })
);
ringMesh.rotation.x = -Math.PI / 2;
reticleGroup.add(ringMesh);

const innerDisc = new THREE.Mesh(
    new THREE.CircleGeometry(0.35, 32),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.7, side: THREE.DoubleSide })
);
innerDisc.rotation.x = -Math.PI / 2;
reticleGroup.add(innerDisc);

const outerGlow = new THREE.Mesh(
    new THREE.RingGeometry(0.58, 0.7, 48),
    new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
);
outerGlow.rotation.x = -Math.PI / 2;
reticleGroup.add(outerGlow);

reticle = reticleGroup;
reticle.matrixAutoUpdate = true;
reticle.visible = true;  // ALWAYS visible from start
scene.add(reticle);

// Set initial position 2m in front of camera
const initialReticlePos = new THREE.Vector3(0, 1, -2);
camera.getWorldPosition(initialReticlePos);
reticle.position.copy(initialReticlePos);

// 2. Request hit-test with SAME reference space
let referenceSpace = null;
try {
  referenceSpace = await session.requestReferenceSpace('local-floor');
} catch(e) {
  referenceSpace = await session.requestReferenceSpace('viewer');
}

session.requestHitTestSource({ space: referenceSpace }).then(source => {
  hitTestSource = source;
});

// 3. Update reticle position when hit-test succeeds
if (hitTestSource && frame) {
  const results = frame.getHitTestResults(hitTestSource);
  if (results.length > 0) {
    const pose = results[0].getPose(referenceSpace);
    if (pose && pose.transform.position) {
      reticle.position.set(pose.transform.position.x, pose.transform.position.y, pose.transform.position.z);
    }
  }
}

// 4. Read back via getWorldPosition (NOT matrix.decompose)
function placeDoor() {
  const pos = new THREE.Vector3();
  const quat = new THREE.Quaternion();
  reticle.getWorldPosition(pos);
  reticle.getWorldQuaternion(quat);
  // ... use pos/quaternion ...
}
```

## Status Flow for Users
1. Tap "Enter AR Portal"
2. Cyan ring appears immediately 2m in front of camera
3. User looks at ground → ring jumps to detected surface
4. User taps screen → door drops at ring location
5. If no ground detected after 3 seconds → door places automatically in front of camera

## Files Modified
- `/home/hermes/projects/webxr-portal-door/index.html` (v20260802-markerfix)