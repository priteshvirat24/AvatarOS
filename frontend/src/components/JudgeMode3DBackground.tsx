import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface JudgeMode3DBackgroundProps {
  opacity?: number;
  speedMultiplier?: number;
  activeChapter?: number;
}

export const JudgeMode3DBackground: React.FC<JudgeMode3DBackgroundProps> = ({
  opacity = 0.16,
  speedMultiplier = 1.0,
  activeChapter = 0
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const meshGroupRef = useRef<THREE.Group | null>(null);
  const mousePos = useRef({ x: 0, y: 0, targetX: 0, targetY: 0 });

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 960;
    const height = container.clientHeight || 640;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 6.0;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0); // Transparent background

    container.appendChild(renderer.domElement);

    // 2. Main Group for Swift Movement & Parallax
    const masterGroup = new THREE.Group();
    meshGroupRef.current = masterGroup;
    scene.add(masterGroup);

    // Chapter Color Palette (Signature AvatarOS High-Contrast Light Colors)
    const chapterColors = [
      0x1A73E8, // Ch 1: Blue (DNA)
      0x1A73E8, // Ch 2: Blue (DAG)
      0xD93025, // Ch 3: Red (Safety Gate)
      0xB06000, // Ch 4: Amber (Live Audio)
      0x137333, // Ch 5: Green (ClickHouse MCP)
      0x1A73E8  // Ch 6: Blue (Scorecard)
    ];

    const activeColor = chapterColors[activeChapter % chapterColors.length];

    // 3. Central Wireframe Geodesic Sphere
    const sphereGeo = new THREE.IcosahedronGeometry(2.1, 2);
    const wireframeMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      wireframe: true,
      transparent: true,
      opacity: 0.45
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, wireframeMat);
    masterGroup.add(sphereMesh);

    // 4. Subtle Particle Cloud (Fibonacci Sphere of 400 Nodes)
    const particleCount = 420;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle

    for (let i = 0; i < particleCount; i++) {
      const y = 1 - (i / (particleCount - 1)) * 2;
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;

      const r = 2.4 + (Math.random() - 0.5) * 0.4;
      positions[i * 3] = Math.cos(theta) * radiusAtY * r;
      positions[i * 3 + 1] = y * r;
      positions[i * 3 + 2] = Math.sin(theta) * radiusAtY * r;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      size: 0.045,
      color: activeColor,
      transparent: true,
      opacity: 0.65
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    masterGroup.add(particles);

    // 5. Dual Orbital Rings (Swift Gyroscopic Movement)
    const ringGeo1 = new THREE.TorusGeometry(2.7, 0.012, 16, 120);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: 0x1A73E8,
      transparent: true,
      opacity: 0.35
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    masterGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(3.1, 0.008, 16, 120);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x137333,
      transparent: true,
      opacity: 0.25
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    masterGroup.add(ring2);

    // 6. Swift Drifting Background Nodes
    const streamCount = 100;
    const streamGeo = new THREE.BufferGeometry();
    const streamPositions = new Float32Array(streamCount * 3);
    for (let i = 0; i < streamCount; i++) {
      streamPositions[i * 3] = (Math.random() - 0.5) * 12;
      streamPositions[i * 3 + 1] = (Math.random() - 0.5) * 8;
      streamPositions[i * 3 + 2] = (Math.random() - 0.5) * 6;
    }
    streamGeo.setAttribute('position', new THREE.BufferAttribute(streamPositions, 3));
    const streamMat = new THREE.PointsMaterial({
      size: 0.035,
      color: 0x5F6368,
      transparent: true,
      opacity: 0.35
    });
    const streamParticles = new THREE.Points(streamGeo, streamMat);
    scene.add(streamParticles);

    // Mouse Tracking for Smooth Damped Parallax
    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      mousePos.current.targetX = (x - 0.5) * 1.5;
      mousePos.current.targetY = -(y - 0.5) * 1.5;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // 7. Animation Loop with Swift Movement
    let animId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Swift, smooth rotation of central biometric core
      sphereMesh.rotation.y += 0.35 * delta * speedMultiplier;
      sphereMesh.rotation.x += 0.2 * delta * speedMultiplier;

      // Swift counter-rotation of orbital rings
      ring1.rotation.z += 0.45 * delta * speedMultiplier;
      ring2.rotation.x += 0.3 * delta * speedMultiplier;

      // Particle pulsing
      particles.rotation.y += 0.25 * delta * speedMultiplier;

      // Swift drifting of background nodes
      const streamPos = streamGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < streamCount; i++) {
        streamPos[i * 3 + 1] += 0.25 * delta;
        if (streamPos[i * 3 + 1] > 4) {
          streamPos[i * 3 + 1] = -4;
        }
      }
      streamGeo.attributes.position.needsUpdate = true;

      // Damped mouse parallax
      mousePos.current.x += (mousePos.current.targetX - mousePos.current.x) * 0.06;
      mousePos.current.y += (mousePos.current.targetY - mousePos.current.y) * 0.06;

      masterGroup.position.x = mousePos.current.x * 0.8 + Math.sin(elapsedTime * 0.4) * 0.25;
      masterGroup.position.y = mousePos.current.y * 0.8 + Math.cos(elapsedTime * 0.5) * 0.2;

      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
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
  }, [activeChapter, speedMultiplier]);

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
        transition: 'opacity 0.3s ease'
      }}
      aria-hidden="true"
    />
  );
};

export default JudgeMode3DBackground;
