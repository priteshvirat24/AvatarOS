import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface JudgeMode3DBackgroundProps {
  opacity?: number;
  speedMultiplier?: number;
  activeChapter?: number;
  activePoint?: number;
}

export const JudgeMode3DBackground: React.FC<JudgeMode3DBackgroundProps> = ({
  opacity = 0.75, // Clearly visible on white background
  speedMultiplier = 0.5, // Swift and slow: graceful, smooth, elegant
  activeChapter = 0,
  activePoint = 0
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const targetCamPos = useRef(new THREE.Vector3(0, 0, 5.5));
  const mousePos = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 5.5);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0); // Transparent to blend seamlessly on pure white

    container.appendChild(renderer.domElement);

    // 2. Master Group for 3D Motion
    const masterGroup = new THREE.Group();
    scene.add(masterGroup);

    // Google Light Theme High-Contrast Colors (Vivid against white)
    const chapterColors = [
      0x1A73E8, // Ch 1: Google Blue (Digital DNA)
      0x1A73E8, // Ch 2: Google Blue (Agent DAG)
      0xD93025, // Ch 3: Google Red (Safety Gate)
      0xB06000, // Ch 4: Google Amber (Realtime Voice)
      0x137333, // Ch 5: Google Green (ClickHouse MCP)
      0x1A73E8  // Ch 6: Google Blue (Scorecard)
    ];

    const activeColor = chapterColors[activeChapter % chapterColors.length];

    // 3. Central Biometric Geodesic Wireframe Sphere (Vivid & Clearly Visible)
    const sphereGeo = new THREE.IcosahedronGeometry(1.9, 2);
    const wireframeMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      wireframe: true,
      transparent: true,
      opacity: 0.65 // High visibility on white
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, wireframeMat);
    masterGroup.add(sphereMesh);

    // Inner Crystalline Nucleus
    const innerNucleusGeo = new THREE.OctahedronGeometry(1.0, 1);
    const innerNucleusMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      wireframe: true,
      transparent: true,
      opacity: 0.4
    });
    const innerNucleus = new THREE.Mesh(innerNucleusGeo, innerNucleusMat);
    masterGroup.add(innerNucleus);

    // 4. Fibonacci Neural Particle Cloud (480 Points - Vivid on White)
    const particleCount = 480;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const phi = Math.PI * (3 - Math.sqrt(5));

    for (let i = 0; i < particleCount; i++) {
      const y = 1 - (i / (particleCount - 1)) * 2;
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;

      const r = 2.2 + (Math.random() - 0.5) * 0.5;
      positions[i * 3] = Math.cos(theta) * radiusAtY * r;
      positions[i * 3 + 1] = y * r;
      positions[i * 3 + 2] = Math.sin(theta) * radiusAtY * r;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.055,
      color: activeColor,
      transparent: true,
      opacity: 0.85
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    masterGroup.add(particles);

    // 5. Triple Gyroscopic Orbital Rings (Swift, Smooth, Slow Motion)
    const ringGeo1 = new THREE.TorusGeometry(2.6, 0.016, 16, 120);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: activeColor,
      transparent: true,
      opacity: 0.6
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    masterGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(3.0, 0.012, 16, 120);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x4285F4, // Secondary blue accent
      transparent: true,
      opacity: 0.45
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    masterGroup.add(ring2);

    const ringGeo3 = new THREE.TorusGeometry(3.4, 0.009, 16, 120);
    const ringMat3 = new THREE.MeshBasicMaterial({
      color: 0x137333, // Tertiary green accent
      transparent: true,
      opacity: 0.35
    });
    const ring3 = new THREE.Mesh(ringGeo3, ringMat3);
    ring3.rotation.z = Math.PI / 6;
    masterGroup.add(ring3);

    // 6. Ambient Floating Depth Nodes (Drifting gently across the canvas)
    const dustCount = 120;
    const dustGeo = new THREE.BufferGeometry();
    const dustPositions = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount; i++) {
      dustPositions[i * 3] = (Math.random() - 0.5) * 14;
      dustPositions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      dustPositions[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));
    const dustMat = new THREE.PointsMaterial({
      size: 0.045,
      color: 0x5F6368,
      transparent: true,
      opacity: 0.5
    });
    const dustParticles = new THREE.Points(dustGeo, dustMat);
    scene.add(dustParticles);

    // 7. Camera Angle Shifts per Chapter
    const waypoints = [
      new THREE.Vector3(0.8, 0.3, 5.4),
      new THREE.Vector3(-0.9, -0.2, 5.3),
      new THREE.Vector3(0.0, 0.6, 5.6),
      new THREE.Vector3(1.0, -0.4, 5.2),
      new THREE.Vector3(-0.8, 0.5, 5.5),
      new THREE.Vector3(0.0, 0.0, 5.4)
    ];

    const baseTarget = waypoints[activeChapter % waypoints.length].clone();
    baseTarget.x += (activePoint - 1) * 0.25;
    baseTarget.y += (activePoint - 1) * 0.18;
    targetCamPos.current = baseTarget;

    // Mouse Tracking for Smooth Parallax
    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      mousePos.current.targetX = (x - 0.5) * 1.2;
      mousePos.current.targetY = -(y - 0.5) * 1.2;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // 8. SWIFT AND SLOW Kinetic Animation Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      // Graceful, majestic, slow rotation
      sphereMesh.rotation.y += 0.16 * delta * speedMultiplier;
      sphereMesh.rotation.x += 0.10 * delta * speedMultiplier;

      innerNucleus.rotation.y -= 0.22 * delta * speedMultiplier;
      innerNucleus.rotation.z += 0.14 * delta * speedMultiplier;

      ring1.rotation.z += 0.20 * delta * speedMultiplier;
      ring2.rotation.x += 0.15 * delta * speedMultiplier;
      ring3.rotation.y += 0.12 * delta * speedMultiplier;

      particles.rotation.y += 0.12 * delta * speedMultiplier;

      // Gentle ambient node drift
      const dustArr = dustGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < dustCount; i++) {
        dustArr[i * 3 + 1] += 0.18 * delta;
        if (dustArr[i * 3 + 1] > 5) {
          dustArr[i * 3 + 1] = -5;
        }
      }
      dustGeo.attributes.position.needsUpdate = true;

      // Smooth camera interpolation
      camera.position.lerp(targetCamPos.current, 0.04);

      // Smooth mouse parallax
      mousePos.current.x += (mousePos.current.targetX - mousePos.current.x) * 0.06;
      mousePos.current.y += (mousePos.current.targetY - mousePos.current.y) * 0.06;

      masterGroup.position.x = mousePos.current.x * 0.7;
      masterGroup.position.y = mousePos.current.y * 0.7;

      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      if (container && renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [activeChapter, activePoint, speedMultiplier]);

  return (
    <div
      ref={mountRef}
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 1, // Visible layer right behind the glass cards
        opacity: opacity,
        overflow: 'hidden',
        transition: 'opacity 0.3s ease'
      }}
      aria-hidden="true"
    />
  );
};

export default JudgeMode3DBackground;
