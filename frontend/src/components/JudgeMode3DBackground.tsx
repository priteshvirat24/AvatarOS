import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface JudgeMode3DBackgroundProps {
  opacity?: number;
  speedMultiplier?: number;
  activeChapter?: number;
  activePoint?: number;
}

export const JudgeMode3DBackground: React.FC<JudgeMode3DBackgroundProps> = ({
  opacity = 0.10,
  speedMultiplier = 0.3,
  activeChapter = 0,
  activePoint = 0
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const targetCamPos = useRef(new THREE.Vector3(0, 0, 5.8));
  const mousePos = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 5.8);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    container.appendChild(renderer.domElement);

    // 2. Master Groups
    const masterGroup = new THREE.Group();
    scene.add(masterGroup);

    // Subtle Google Light Colors
    const chapterColors = [
      0x1A73E8, // Blue
      0x1A73E8, // Blue
      0xD93025, // Red
      0xB06000, // Amber
      0x137333, // Green
      0x1A73E8  // Blue
    ];

    const activeColor = chapterColors[activeChapter % chapterColors.length];

    // 3. Central Biometric Wireframe Core (Soft & Elegant)
    const sphereGeo = new THREE.IcosahedronGeometry(1.9, 2);
    const wireframeMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      wireframe: true,
      transparent: true,
      opacity: 0.28
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, wireframeMat);
    masterGroup.add(sphereMesh);

    // 4. Subtle Ambient Particle Cloud (Soft Fibonacci Sphere)
    const particleCount = 380;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const phi = Math.PI * (3 - Math.sqrt(5));

    for (let i = 0; i < particleCount; i++) {
      const y = 1 - (i / (particleCount - 1)) * 2;
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;

      const r = 2.2 + (Math.random() - 0.5) * 0.4;
      positions[i * 3] = Math.cos(theta) * radiusAtY * r;
      positions[i * 3 + 1] = y * r;
      positions[i * 3 + 2] = Math.sin(theta) * radiusAtY * r;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.04,
      color: activeColor,
      transparent: true,
      opacity: 0.45
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    masterGroup.add(particles);

    // 5. Dual Gyroscopic Orbital Rings (Slow & Graceful)
    const ringGeo1 = new THREE.TorusGeometry(2.7, 0.008, 16, 120);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: activeColor,
      transparent: true,
      opacity: 0.22
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    masterGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(3.1, 0.006, 16, 120);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x5F6368,
      transparent: true,
      opacity: 0.15
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    masterGroup.add(ring2);

    // 6. Slow Floating Ambient Dust
    const dustCount = 80;
    const dustGeo = new THREE.BufferGeometry();
    const dustPositions = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount; i++) {
      dustPositions[i * 3] = (Math.random() - 0.5) * 12;
      dustPositions[i * 3 + 1] = (Math.random() - 0.5) * 8;
      dustPositions[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));
    const dustMat = new THREE.PointsMaterial({
      size: 0.03,
      color: 0x80868B,
      transparent: true,
      opacity: 0.25
    });
    const dustParticles = new THREE.Points(dustGeo, dustMat);
    scene.add(dustParticles);

    // Subtle Waypoint offsets for camera
    const waypoints = [
      new THREE.Vector3(0.6, 0.2, 5.6),
      new THREE.Vector3(-0.6, -0.2, 5.5),
      new THREE.Vector3(0.0, 0.5, 5.7),
      new THREE.Vector3(0.7, -0.3, 5.4),
      new THREE.Vector3(-0.5, 0.4, 5.6),
      new THREE.Vector3(0.0, 0.0, 5.5)
    ];

    const baseTarget = waypoints[activeChapter % waypoints.length].clone();
    baseTarget.x += (activePoint - 1) * 0.2;
    baseTarget.y += (activePoint - 1) * 0.15;
    targetCamPos.current = baseTarget;

    // Mouse Tracking for Gentle Parallax
    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      mousePos.current.targetX = (x - 0.5) * 0.8;
      mousePos.current.targetY = -(y - 0.5) * 0.8;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // 7. Slow, Swift, Non-Distracting Animation Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      // Very slow, smooth, graceful rotation
      sphereMesh.rotation.y += 0.07 * delta * speedMultiplier;
      sphereMesh.rotation.x += 0.04 * delta * speedMultiplier;

      ring1.rotation.z += 0.09 * delta * speedMultiplier;
      ring2.rotation.x += 0.06 * delta * speedMultiplier;

      particles.rotation.y += 0.05 * delta * speedMultiplier;

      // Slow ambient dust drift
      const dustArr = dustGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < dustCount; i++) {
        dustArr[i * 3 + 1] += 0.08 * delta;
        if (dustArr[i * 3 + 1] > 4) {
          dustArr[i * 3 + 1] = -4;
        }
      }
      dustGeo.attributes.position.needsUpdate = true;

      // Gentle camera lerp
      camera.position.lerp(targetCamPos.current, 0.03);

      // Gentle mouse parallax
      mousePos.current.x += (mousePos.current.targetX - mousePos.current.x) * 0.05;
      mousePos.current.y += (mousePos.current.targetY - mousePos.current.y) * 0.05;

      masterGroup.position.x = mousePos.current.x * 0.4;
      masterGroup.position.y = mousePos.current.y * 0.4;

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
        zIndex: 0,
        opacity: opacity,
        overflow: 'hidden',
        transition: 'opacity 0.4s ease'
      }}
      aria-hidden="true"
    />
  );
};

export default JudgeMode3DBackground;
