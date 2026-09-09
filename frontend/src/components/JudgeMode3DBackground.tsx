import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface JudgeMode3DBackgroundProps {
  opacity?: number;
  speedMultiplier?: number;
  activeChapter?: number;
  activePoint?: number;
}

export const JudgeMode3DBackground: React.FC<JudgeMode3DBackgroundProps> = ({
  opacity = 0.45,
  speedMultiplier = 1.2,
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
    renderer.setClearColor(0x000000, 0);

    container.appendChild(renderer.domElement);

    // 2. Master Groups
    const masterGroup = new THREE.Group();
    scene.add(masterGroup);

    // Chapter Color Themes (AvatarOS Signature Palette)
    const chapterColors = [
      0x1A73E8, // Ch 1: Electric Blue (Digital DNA)
      0x1A73E8, // Ch 2: Blue (Agent DAG)
      0xD93025, // Ch 3: Warning Red (Safety Gate)
      0xB06000, // Ch 4: Warm Amber (Realtime Live)
      0x137333, // Ch 5: Emerald Green (ClickHouse MCP)
      0x1A73E8  // Ch 6: Cyan/Blue (Scorecard)
    ];

    const activeColor = chapterColors[activeChapter % chapterColors.length];

    // 3. Central Biometric Wireframe Core
    const sphereGeo = new THREE.IcosahedronGeometry(1.8, 3);
    const wireframeMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      wireframe: true,
      transparent: true,
      opacity: 0.55
    });
    const sphereMesh = new THREE.Mesh(sphereGeo, wireframeMat);
    masterGroup.add(sphereMesh);

    // Inner Glowing Core
    const innerCoreGeo = new THREE.SphereGeometry(1.1, 24, 24);
    const innerCoreMat = new THREE.MeshBasicMaterial({
      color: activeColor,
      transparent: true,
      opacity: 0.18
    });
    const innerCore = new THREE.Mesh(innerCoreGeo, innerCoreMat);
    masterGroup.add(innerCore);

    // 4. Fibonacci Neural Particle Cloud (600 Points)
    const particleCount = 600;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const baseColor = new THREE.Color(activeColor);
    const whiteColor = new THREE.Color(0xFFFFFF);

    const phi = Math.PI * (3 - Math.sqrt(5));

    for (let i = 0; i < particleCount; i++) {
      const y = 1 - (i / (particleCount - 1)) * 2;
      const radiusAtY = Math.sqrt(1 - y * y);
      const theta = phi * i;

      const r = 2.1 + (Math.random() - 0.5) * 0.6;
      positions[i * 3] = Math.cos(theta) * radiusAtY * r;
      positions[i * 3 + 1] = y * r;
      positions[i * 3 + 2] = Math.sin(theta) * radiusAtY * r;

      const mixed = baseColor.clone().lerp(whiteColor, Math.random() * 0.4);
      colors[i * 3] = mixed.r;
      colors[i * 3 + 1] = mixed.g;
      colors[i * 3 + 2] = mixed.b;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMat = new THREE.PointsMaterial({
      size: 0.05,
      vertexColors: true,
      transparent: true,
      opacity: 0.8
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    masterGroup.add(particles);

    // 5. Triple Swift Gyroscopic Orbital Rings
    const ringGeo1 = new THREE.TorusGeometry(2.5, 0.012, 16, 120);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: activeColor,
      transparent: true,
      opacity: 0.45
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    masterGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(2.9, 0.009, 16, 120);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x4285F4,
      transparent: true,
      opacity: 0.35
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    masterGroup.add(ring2);

    const ringGeo3 = new THREE.TorusGeometry(3.3, 0.007, 16, 120);
    const ringMat3 = new THREE.MeshBasicMaterial({
      color: 0x34A853,
      transparent: true,
      opacity: 0.3
    });
    const ring3 = new THREE.Mesh(ringGeo3, ringMat3);
    ring3.rotation.z = Math.PI / 6;
    masterGroup.add(ring3);

    // 6. Swift Warp Particles (Flying Toward Camera - Cinematic Depth)
    const warpCount = 240;
    const warpGeo = new THREE.BufferGeometry();
    const warpPositions = new Float32Array(warpCount * 3);
    for (let i = 0; i < warpCount; i++) {
      warpPositions[i * 3] = (Math.random() - 0.5) * 14;
      warpPositions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      warpPositions[i * 3 + 2] = (Math.random() - 0.5) * 12;
    }
    warpGeo.setAttribute('position', new THREE.BufferAttribute(warpPositions, 3));
    const warpMat = new THREE.PointsMaterial({
      size: 0.045,
      color: 0x1A73E8,
      transparent: true,
      opacity: 0.55
    });
    const warpParticles = new THREE.Points(warpGeo, warpMat);
    scene.add(warpParticles);

    // 7. Dynamic Camera Waypoints for Cinematic Angle Shifts
    const waypoints = [
      new THREE.Vector3(1.4, 0.4, 5.2),   // Ch 0: High-tech angled view
      new THREE.Vector3(-1.6, -0.3, 5.0), // Ch 1: Left dramatic angle
      new THREE.Vector3(0.0, 1.2, 5.4),   // Ch 2: Warning elevated view
      new THREE.Vector3(1.8, -0.5, 4.8),  // Ch 3: Intimate live angle
      new THREE.Vector3(-1.4, 0.8, 5.2),  // Ch 4: Analytical top-left angle
      new THREE.Vector3(0.0, 0.0, 5.0)    // Ch 5: Hero center alignment
    ];

    // Sub-nudge for points (0, 1, 2)
    const baseTarget = waypoints[activeChapter % waypoints.length].clone();
    baseTarget.x += (activePoint - 1) * 0.4;
    baseTarget.y += (activePoint - 1) * 0.25;
    targetCamPos.current = baseTarget;

    // Mouse Tracking for Smooth Parallax
    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;
      mousePos.current.targetX = (x - 0.5) * 1.8;
      mousePos.current.targetY = -(y - 0.5) * 1.8;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // 8. Kinetic Animation Loop with Swift Rhythms
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      // Swift rotation
      sphereMesh.rotation.y += 0.55 * delta * speedMultiplier;
      sphereMesh.rotation.x += 0.35 * delta * speedMultiplier;

      ring1.rotation.z += 0.7 * delta * speedMultiplier;
      ring2.rotation.x += 0.5 * delta * speedMultiplier;
      ring3.rotation.y += 0.4 * delta * speedMultiplier;

      particles.rotation.y += 0.4 * delta * speedMultiplier;

      // Pulse inner core with breathing rhythm
      const pulse = 1 + Math.sin(elapsedTime * 3) * 0.08;
      innerCore.scale.set(pulse, pulse, pulse);

      // Swift warp particles rushing forward (Z-axis motion toward viewer)
      const warpArr = warpGeo.attributes.position.array as Float32Array;
      for (let i = 0; i < warpCount; i++) {
        warpArr[i * 3 + 2] += 2.8 * delta * speedMultiplier;
        if (warpArr[i * 3 + 2] > 6) {
          warpArr[i * 3 + 2] = -6;
          warpArr[i * 3] = (Math.random() - 0.5) * 14;
          warpArr[i * 3 + 1] = (Math.random() - 0.5) * 10;
        }
      }
      warpGeo.attributes.position.needsUpdate = true;

      // Smooth camera swoop towards chapter target waypoint
      camera.position.lerp(targetCamPos.current, 0.05);

      // Smooth mouse parallax damping
      mousePos.current.x += (mousePos.current.targetX - mousePos.current.x) * 0.08;
      mousePos.current.y += (mousePos.current.targetY - mousePos.current.y) * 0.08;

      masterGroup.position.x = mousePos.current.x * 0.9;
      masterGroup.position.y = mousePos.current.y * 0.9;

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
