import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Sparkles, Activity, ShieldCheck, Cpu, Radio, Maximize2 } from 'lucide-react';

interface GoogleLabs3DProps {
  characterName?: string;
  characterVersion?: string;
  isSpeaking?: boolean;
  isListening?: boolean;
  energy?: number;
  interactive?: boolean;
  height?: string | number;
}

export const GoogleLabs3D: React.FC<GoogleLabs3DProps> = ({
  characterName = "Maya",
  characterVersion = "v1.7.0",
  isSpeaking = false,
  isListening = false,
  energy = 0.78,
  interactive = true,
  height = "100%"
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [fps, setFps] = useState<number>(60);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 5.2;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Google Signature Colors Palette for Shaders / Particles (Light Theme Contrast)
    const googleColors = [
      new THREE.Color('#1A73E8'), // Google Blue
      new THREE.Color('#D93025'), // Google Red
      new THREE.Color('#B06000'), // Google Yellow / Amber
      new THREE.Color('#137333'), // Google Green
      new THREE.Color('#007B83'), // Google Teal / Cyan
    ];

    // 1. Central Icosahedron Wireframe (Neural Core)
    const icoGeometry = new THREE.IcosahedronGeometry(1.35, 2);
    const icoMaterial = new THREE.MeshBasicMaterial({
      color: 0x1a73e8,
      wireframe: true,
      transparent: true,
      opacity: 0.45,
    });
    const icoMesh = new THREE.Mesh(icoGeometry, icoMaterial);
    scene.add(icoMesh);

    // 2. Inner Glowing Core Sphere
    const innerGeo = new THREE.SphereGeometry(0.85, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x4285f4,
      wireframe: true,
      transparent: true,
      opacity: 0.3,
    });
    const innerCore = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerCore);

    // 3. Google Particle Cloud (600 Neural Synapse Nodes)
    const particleCount = 650;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const originalPositions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      // Fibonacci sphere distribution
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;
      const radius = 1.9 + (Math.random() - 0.5) * 0.45;

      const x = radius * Math.cos(theta) * Math.sin(phi);
      const y = radius * Math.sin(theta) * Math.sin(phi);
      const z = radius * Math.cos(phi);

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      originalPositions[i * 3] = x;
      originalPositions[i * 3 + 1] = y;
      originalPositions[i * 3 + 2] = z;

      const assignedColor = googleColors[i % googleColors.length];
      colors[i * 3] = assignedColor.r;
      colors[i * 3 + 1] = assignedColor.g;
      colors[i * 3 + 2] = assignedColor.b;
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle Material
    const particleMat = new THREE.PointsMaterial({
      size: 0.055,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // 4. Orbiting Rings (Avatar Gyroscopic Axis)
    const ringGeo1 = new THREE.TorusGeometry(2.3, 0.008, 16, 100);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x4285f4, transparent: true, opacity: 0.4 });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    scene.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(2.5, 0.008, 16, 100);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x34a853, transparent: true, opacity: 0.35 });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    scene.add(ring2);

    // Mouse Tracking with Damping
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
    };

    container.addEventListener('mousemove', handleMouseMove);

    // Resize Handler
    const handleResize = () => {
      if (!container) return;
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    window.addEventListener('resize', handleResize);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();
    let frameCount = 0;
    let lastTime = performance.now();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      // Measure FPS
      frameCount++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(Math.round((frameCount * 1000) / (now - lastTime)));
        frameCount = 0;
        lastTime = now;
      }

      // Smooth mouse damping
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;

      // Base rotation
      const speechIntensity = isSpeaking ? 2.5 : isListening ? 1.6 : 1.0;
      icoMesh.rotation.y += 0.008 * speechIntensity;
      icoMesh.rotation.x += 0.004 * speechIntensity;

      innerCore.rotation.y -= 0.012 * speechIntensity;
      particleSystem.rotation.y += 0.005 * speechIntensity;
      particleSystem.rotation.z += 0.002;

      ring1.rotation.z += 0.006;
      ring2.rotation.x += 0.005;

      // Reactivity: pulse vertices based on speech/energy
      const posAttr = particleGeo.attributes.position as THREE.BufferAttribute;
      const currentPos = posAttr.array as Float32Array;

      const waveSpeed = isSpeaking ? 6 : 2;
      const waveAmp = (isSpeaking ? 0.22 : 0.06) * energy;

      for (let i = 0; i < particleCount; i++) {
        const ox = originalPositions[i * 3];
        const oy = originalPositions[i * 3 + 1];
        const oz = originalPositions[i * 3 + 2];

        const dist = Math.sqrt(ox * ox + oy * oy + oz * oz);
        const wave = Math.sin(dist * 4 - time * waveSpeed) * waveAmp;

        currentPos[i * 3] = ox * (1 + wave);
        currentPos[i * 3 + 1] = oy * (1 + wave);
        currentPos[i * 3 + 2] = oz * (1 + wave);
      }
      posAttr.needsUpdate = true;

      // Camera tilt from mouse
      camera.position.x = targetX * 1.2;
      camera.position.y = targetY * 1.2;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);

      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }

      icoGeometry.dispose();
      icoMaterial.dispose();
      innerGeo.dispose();
      innerMat.dispose();
      particleGeo.dispose();
      particleMat.dispose();
      ringGeo1.dispose();
      ringMat1.dispose();
      ringGeo2.dispose();
      ringMat2.dispose();
      renderer.dispose();
    };
  }, [isSpeaking, isListening, energy, interactive]);

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: height,
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        overflow: 'hidden',
        border: '1px solid #DADCE0',
        boxShadow: '0 1px 3px rgba(60,64,67,0.12)',
        display: 'flex',
        flexDirection: 'column',
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 3D WebGL Canvas Container */}
      <div ref={mountRef} style={{ width: '100%', height: '100%', flex: 1, cursor: 'grab' }} />

      {/* Avatar Core HUD Overlays */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          pointerEvents: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(12px)',
              padding: '4px 12px',
              borderRadius: '9999px',
              border: '1px solid #DADCE0',
              boxShadow: '0 1px 3px rgba(60,64,67,0.15)',
            }}
          >
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isSpeaking ? '#D93025' : isListening ? '#B06000' : '#137333',
                boxShadow: `0 0 6px ${isSpeaking ? '#D93025' : isListening ? '#B06000' : '#137333'}`,
              }}
            />
            <span style={{ fontSize: '11px', fontWeight: 600, color: '#202124', letterSpacing: '0.2px' }}>
              {characterName.toUpperCase()} {characterVersion}
            </span>
          </div>

          <div
            style={{
              backgroundColor: '#E8F0FE',
              border: '1px solid #D2E3FC',
              padding: '4px 10px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Cpu size={12} color="#1A73E8" />
            <span style={{ fontSize: '10px', fontWeight: 600, color: '#1A73E8' }}>
              GEMINI NEURAL CORE
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', color: '#5F6368' }}>
          <span>FPS: {fps}</span>
          <span>•</span>
          <span style={{ color: '#137333', fontWeight: 600 }}>DNA SEALED</span>
        </div>
      </div>

      {/* Bottom Status Ticker */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          right: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(12px)',
            padding: '6px 14px',
            borderRadius: '9999px',
            border: '1px solid #DADCE0',
            boxShadow: '0 1px 3px rgba(60,64,67,0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            color: '#202124',
          }}
        >
          <Activity size={12} color="#137333" />
          <span>
            {isSpeaking
              ? "Synthesizing Neural Speech Waveform..."
              : isListening
              ? "Listening to Real-Time Multimodal Audio..."
              : "Neural Hologram Active • Drag to inspect spatial vector mesh"}
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(12px)',
            padding: '6px 14px',
            borderRadius: '9999px',
            border: '1px solid #DADCE0',
            boxShadow: '0 1px 3px rgba(60,64,67,0.15)',
            fontSize: '10px',
            color: '#5F6368',
          }}
        >
          <span style={{ color: '#1A73E8' }}>●</span>
          <span style={{ color: '#D93025' }}>●</span>
          <span style={{ color: '#B06000' }}>●</span>
          <span style={{ color: '#137333' }}>●</span>
          <span style={{ marginLeft: '4px', fontWeight: 600 }}>NEURAL AVATAR 3D CORE</span>
        </div>
      </div>
    </div>
  );
};

export default GoogleLabs3D;
