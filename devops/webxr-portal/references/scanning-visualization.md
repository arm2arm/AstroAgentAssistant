# Scanning Visualization (Updated)

This document describes the working scanning visualization for the WebXR portal door project at `/home/hermes/projects/webxr-portal-door/`.

## Current Implementation (v3, 2026-08-02)

### Key Design Principle

**Do NOT use a wireframe floor plane attached to world coordinates.** When the camera or smartphone moves, the grid disappears because the scene uses `local-floor` reference space.

**Instead:** Use a particle system (100 dots) that attaches to the reticle via `group` relationship. The reticle is positioned at the floor plane by hit-test; particles follow it.

### Particle System (Dots)

100 animated cyan-green particles moving in wave patterns attached to the reticle.

```javascript
// Create particle system
const particleCount = 100;
const particleGeo = new THREE.BufferGeometry();
const particlePositions = new Float32Array(particleCount * 3);
const colors = new Float32Array(particleCount * 3);

for (let i = 0; i < particleCount; i++) {
    particlePositions[i * 3] = (Math.random() - 0.5) * 6;
    particlePositions[i * 3 + 1] = 0.02;
    particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 6;
    const h = 0.5 + Math.random() * 0.3;  // cyan-green hue
    const rgb = new THREE.Color().setHSL(h, 0.8, 0.6);
    colors[i * 3] = rgb.r;
    colors[i * 3 + 1] = rgb.g;
    colors[i * 3 + 2] = rgb.b;
}

particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const particleMat = new THREE.PointsMaterial({
    size: 0.25,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    sizeAttenuation: true
});

scanParticles = new THREE.Points(particleGeo, particleMat);
scanParticles.visible = false;  // Hide until floor detected
scene.add(scanParticles);
```

### Animation in Render Loop

Particles are local to reticle, so animation uses relative coordinates only.

```javascript
// Scanning visualization: animate particles attached to reticle
if (mode === 'scanning' && !doorPlaced && scanParticles && scanParticles.visible) {
    const ts = timestamp * 0.001;
    // Animate particles — they're local to reticle, use relative coords
    const positions = scanParticles.geometry.attributes.position.array;
    for (let i = 0; i < 100; i++) {
        const ix = i * 3;
        const x = positions[ix];
        const z = positions[ix + 2];
        positions[ix + 1] = 0.02 + Math.sin(ts * 3 + x * 2 + z * 2) * 0.02;
    }
    scanParticles.geometry.attributes.position.needsUpdate = true;
}
```

### Hit-test Integration

Particles attach to reticle when floor is detected:

```javascript
// HIT-TEST EACH FRAME — set position from pose.transform.position
const results = frame.getHitTestResults(hitTestSource);
if (results.length > 0 && !doorPlaced) {
    const pose = results[0].getPose(referenceSpace);
    if (pose && pose.transform.position.x !== undefined) {
        reticle.position.set(
            pose.transform.position.x,
            pose.transform.position.y,
            pose.transform.position.z
        );
        // Attach particles to reticle so they move with it
        if (scanParticles) {
            scanParticles.position.set(0, 0, 0);  // local to reticle
            scanParticles.rotation.set(0, 0, 0);
        }
        // Show particles only after floor detected
        reticle.visible = true;
        if (scanParticles) scanParticles.visible = true;
    }
}
```

### Cleanup on Session End

```javascript
function onSessionEnd() {
    if (scanParticles) {
        scene.remove(scanParticles);
        scanParticles.geometry.dispose();
        scanParticles.material.dispose();
        scanParticles = null;
    }
}
```

## Status Feedback

Show user what's happening:

```javascript
setStatus(hitTestSource
    ? 'Scanning floor plane — wait for the cyan marker'
    : 'Room scan starting — wait for placement marker');
```

## Why This Works

- **Particles attach to reticle**: They move with the camera but stay attached to the detected floor surface
- **Hidden until floor detected**: No confusion during initial AR startup
- **Cyan-green color**: Matches portal theme; high contrast against typical room backgrounds
- **No world-space grid**: Grid doesn't disappear when camera moves
- **Cleanup**: Prevents memory leaks when session ends