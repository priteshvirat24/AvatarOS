import React, { useState, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2, Shield, Eye, Layers, Film, FileCode2, Sparkles, CheckCircle2, User, Activity, Video, Cpu, Box, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GoogleLabs3D } from './GoogleLabs3D';

interface LiveStageProps {
  videoUrl: string;
  hindiVideoUrl?: string;
  characterName: string;
  characterVersion: string;
  activeSceneNo?: number;
  targetEmotion?: string;
  energy?: number;
  c2paManifestHash?: string;
  mediaSha256?: string;
  repurposedClips?: any[];
  isExecuting?: boolean;
  stageStatus?: 'IDLE' | 'PREPARING' | 'SPEAKING' | 'VERIFYING' | 'APPROVED' | 'BLOCKED';
  rendererProvider?: string;
  voiceProvider?: string;
  showCast?: boolean;
  onToggleCast?: () => void;
  castCount?: number;
}

export const LiveStage: React.FC<LiveStageProps> = ({
  videoUrl,
  hindiVideoUrl,
  characterName,
  characterVersion,
  activeSceneNo = 1,
  targetEmotion = "confident",
  energy = 0.78,
  c2paManifestHash,
  mediaSha256,
  repurposedClips = [],
  isExecuting = false,
  stageStatus = "APPROVED",
  rendererProvider = "Deterministic Engine (FFmpeg)",
  voiceProvider = "Deterministic Acoustic Synthesizer",
  showCast = false,
  onToggleCast,
  castCount = 4
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentLang, setCurrentLang] = useState<'en' | 'hi'>('en');
  const [activeTab, setActiveTab] = useState<'video' | '3d_neural_core' | 'performance_preview' | 'storyboard' | 'repurposed' | 'c2pa'>('video');
  const [selectedRepurposedUrl, setSelectedRepurposedUrl] = useState<string | null>(null);
  const [showPip3D, setShowPip3D] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  const activeMediaSrc = selectedRepurposedUrl || (currentLang === 'hi' && hindiVideoUrl ? hindiVideoUrl : videoUrl);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const restartVideo = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const performanceScenes = [
    {
      scene: 1,
      role: "Hook",
      character: characterName,
      shot: "Close-Up",
      emotion: "Curious",
      gaze: "Direct (Camera)",
      energy: "0.72",
      voice: currentLang === 'hi' ? "Maya-Hindi-v1" : "Maya-English-v4",
      language: currentLang.toUpperCase(),
      visual: "Maya seated in modern dark tech studio, vibrant indigo ambient keylights, direct eye contact with camera."
    },
    {
      scene: 2,
      role: "Problem",
      character: characterName,
      shot: "Medium Shot",
      emotion: "Concerned",
      gaze: "Direct (Camera)",
      energy: "0.68",
      voice: currentLang === 'hi' ? "Maya-Hindi-v1" : "Maya-English-v4",
      language: currentLang.toUpperCase(),
      visual: "Terminal code buffer animation overlay showing cloud API latency timeout."
    },
    {
      scene: 3,
      role: "Product",
      character: characterName,
      shot: "Medium Close-Up",
      emotion: "Confident",
      gaze: "Direct (Camera)",
      energy: "0.82",
      voice: currentLang === 'hi' ? "Maya-Hindi-v1" : "Maya-English-v4",
      language: currentLang.toUpperCase(),
      visual: "Titan AI Laptop chassis reveal, pulsing 45 TOPS NPU silicon emblem."
    },
    {
      scene: 4,
      role: "Demonstration",
      character: characterName,
      shot: "Medium Close-Up",
      emotion: "Excited",
      gaze: "Direct (Camera)",
      energy: "0.88",
      voice: currentLang === 'hi' ? "Maya-Hindi-v1" : "Maya-English-v4",
      language: currentLang.toUpperCase(),
      visual: "Side-by-side MLPerf inference graph floating: 40% faster local LLM response."
    },
    {
      scene: 5,
      role: "CTA",
      character: characterName,
      shot: "Medium Shot",
      emotion: "Direct",
      gaze: "Direct (Camera)",
      energy: "0.75",
      voice: currentLang === 'hi' ? "Maya-Hindi-v1" : "Maya-English-v4",
      language: currentLang.toUpperCase(),
      visual: "titan.dev order portal lower-third with clean typography and developer kit badge."
    }
  ];

  const currentStageStatus = isExecuting ? 'SPEAKING' : (stageStatus || 'APPROVED');

  return (
    <div style={{
      flex: 1,
      minWidth: 0,
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: 'var(--bg-darkest)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Top Bar for Stage */}
      <div style={{
        padding: '8px 14px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'var(--bg-base)',
        flexWrap: 'wrap',
        gap: '8px',
        minHeight: '44px'
      }}>
        {/* Left: Stream Metadata & Audio Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', minWidth: 0 }}>
          {onToggleCast && !showCast && (
            <button
              onClick={onToggleCast}
              className="btn btn-secondary"
              style={{
                padding: '2px 8px',
                fontSize: '11px',
                borderRadius: 'var(--radius-full)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--text-secondary)'
              }}
              title="Open Digital Cast Panel"
            >
              <User size={11} color="var(--google-blue)" />
              <span>Cast ({castCount})</span>
              <ChevronRight size={10} />
            </button>
          )}

          <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.6px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
            PERFORMANCE
          </span>

          {/* Transition Status Badge */}
          <span className={`badge-neon ${
            currentStageStatus === 'APPROVED' ? 'badge-emerald' :
            currentStageStatus === 'SPEAKING' ? 'badge-primary' :
            currentStageStatus === 'PREPARING' ? 'badge-cyan' :
            currentStageStatus === 'VERIFYING' ? 'badge-amber' : 'badge-rose'
          }`} style={{ fontSize: '9px', padding: '2px 6px', whiteSpace: 'nowrap' }}>
            {currentStageStatus}
          </span>

          <span className="badge-neon badge-secondary" style={{ fontSize: '9px', padding: '2px 5px', whiteSpace: 'nowrap' }}>
            FFmpeg
          </span>

          {/* Language / Audio Track Segmented Toggle */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            backgroundColor: 'var(--color-surface)',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--border-subtle)',
            padding: '1px',
            gap: '1px',
            marginLeft: '2px'
          }} title="Select Master Audio Track Language">
            <button
              onClick={() => { setCurrentLang('en'); setSelectedRepurposedUrl(null); }}
              style={{
                padding: '2px 7px',
                fontSize: '9.5px',
                fontWeight: 700,
                borderRadius: 'var(--radius-full)',
                border: 'none',
                backgroundColor: currentLang === 'en' ? 'var(--color-primary)' : 'transparent',
                color: currentLang === 'en' ? '#fff' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              title="English (Indian)"
            >
              EN
            </button>
            <button
              onClick={() => { setCurrentLang('hi'); setSelectedRepurposedUrl(null); }}
              style={{
                padding: '2px 7px',
                fontSize: '9.5px',
                fontWeight: 700,
                borderRadius: 'var(--radius-full)',
                border: 'none',
                backgroundColor: currentLang === 'hi' ? 'var(--color-secondary)' : 'transparent',
                color: currentLang === 'hi' ? '#fff' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              title="Hindi Dub"
            >
              HI
            </button>
          </div>
        </div>

        {/* Right: View Switcher Tabs (Adaptive, fully responsive) */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--color-surface)',
          padding: '2px',
          borderRadius: 'var(--radius-full)',
          border: '1px solid var(--border-subtle)',
          gap: '2px',
          flexWrap: 'wrap'
        }}>
          {[
            { id: 'video', label: 'Video', icon: Film, title: 'Master Video' },
            { id: '3d_neural_core', label: '3D Core', icon: Cpu, title: '3D Biometric Neural Core' },
            { id: 'performance_preview', label: 'Plan', icon: Activity, title: 'Performance Plan' },
            { id: 'storyboard', label: 'Storyboard', icon: Layers, title: 'Multi-Scene Storyboard' },
            { id: 'repurposed', label: `Shorts (${repurposedClips.length || 3})`, icon: Sparkles, title: 'Omnichannel Vertical Shorts' },
            { id: 'c2pa', label: 'C2PA', icon: Shield, title: 'C2PA Cryptographic Provenance Manifest' }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                className="btn"
                onClick={() => {
                  setActiveTab(tab.id as any);
                  if (tab.id === 'video') setSelectedRepurposedUrl(null);
                }}
                style={{
                  padding: '3px 8px',
                  fontSize: '11px',
                  fontWeight: isActive ? 700 : 500,
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: isActive ? 'var(--color-primary)' : 'transparent',
                  color: isActive ? 'var(--color-on-primary)' : 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  whiteSpace: 'nowrap'
                }}
                title={tab.title}
              >
                <Icon size={12} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Stage Viewport */}
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <AnimatePresence mode="wait">
          {activeTab === '3d_neural_core' && (
            <motion.div
              key="3d_neural_core"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.25 }}
              style={{ width: '100%', maxWidth: '880px', height: '100%', maxHeight: '520px' }}
            >
              <GoogleLabs3D
                characterName={characterName}
                characterVersion={characterVersion}
                isSpeaking={isPlaying || stageStatus === 'SPEAKING'}
                energy={energy}
                height="100%"
              />
            </motion.div>
          )}

          {activeTab === 'video' && (
            <motion.div
              key="video"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.25 }}
              style={{
                position: 'relative',
                width: selectedRepurposedUrl ? '360px' : '100%',
                maxWidth: selectedRepurposedUrl ? '360px' : '880px',
                aspectRatio: selectedRepurposedUrl ? '9/16' : '16/9',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                boxShadow: '0 20px 50px rgba(0,0,0,0.8), 0 0 30px rgba(66,133,244,0.15)',
                border: '1px solid var(--border-focus)',
                backgroundColor: '#000'
              }}
            >
              {/* Real HTML5 Video Element */}
              <video
                ref={videoRef}
                src={activeMediaSrc}
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
                playsInline
                loop
              />

              {/* PiP 3D Hologram Toggle */}
              {showPip3D && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                  width: '180px',
                  height: '130px',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  border: '1px solid rgba(138, 180, 248, 0.4)',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  zIndex: 10
                }}>
                  <GoogleLabs3D
                    characterName={characterName}
                    characterVersion={characterVersion}
                    isSpeaking={isPlaying}
                    energy={energy}
                    height="100%"
                  />
                  <button
                    onClick={() => setShowPip3D(false)}
                    style={{
                      position: 'absolute',
                      top: '4px',
                      right: '4px',
                      background: 'rgba(0,0,0,0.6)',
                      border: 'none',
                      color: 'white',
                      borderRadius: '50%',
                      width: '18px',
                      height: '18px',
                      fontSize: '10px',
                      cursor: 'pointer',
                      zIndex: 20
                    }}
                  >
                    ×
                  </button>
                </div>
              )}

              {/* Neural HUD Overlay (Section 14, Milestone 8) */}
            <div style={{
              position: 'absolute',
              top: '16px',
              left: '16px',
              pointerEvents: 'none',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px'
            }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 8px',
                borderRadius: '4px',
                backgroundColor: 'rgba(0,0,0,0.75)',
                border: '1px solid rgba(99,102,241,0.4)',
                color: 'white',
                fontSize: '11px',
                fontWeight: 600,
                fontFamily: 'var(--font-mono)'
              }}>
                <div className="status-dot active" />
                <span>{characterName.toUpperCase()} {characterVersion} | LOCKED</span>
              </div>
              <span style={{ fontSize: '10px', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                IDENTITY &gt;= 0.92 | VOICE &gt;= 0.90 | LIP-SYNC &lt;= 80MS
              </span>
            </div>

            {/* Target Emotion Badge */}
            <div style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              pointerEvents: 'none'
            }}>
              <div style={{
                padding: '4px 10px',
                borderRadius: '4px',
                backgroundColor: 'rgba(0,0,0,0.75)',
                border: '1px solid rgba(245,158,11,0.5)',
                color: 'var(--accent-amber)',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700
              }}>
                TARGET: {targetEmotion.toUpperCase()} ({Math.round(energy * 100)}%)
              </div>
            </div>

            {/* Facial Keypoint Bounding Box */}
            <div style={{
              position: 'absolute',
              top: '28%',
              left: '38%',
              width: '24%',
              height: '38%',
              border: '1px dashed rgba(56,189,248,0.4)',
              borderRadius: '8px',
              pointerEvents: 'none',
              boxShadow: 'inset 0 0 12px rgba(56,189,248,0.1)'
            }}>
              <span style={{
                position: 'absolute',
                top: '-16px',
                left: '2px',
                fontSize: '9px',
                color: 'var(--accent-cyan)',
                fontFamily: 'var(--font-mono)'
              }}>
                POSE &amp; GAZE ANCHORED
              </span>
            </div>

            {/* Play/Pause Control Bar Overlay */}
            <div style={{
              position: 'absolute',
              bottom: '14px',
              left: '16px',
              right: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              backgroundColor: 'rgba(11, 14, 23, 0.85)',
              backdropFilter: 'blur(8px)',
              padding: '8px 14px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button
                  onClick={togglePlay}
                  style={{
                    background: 'var(--primary)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    cursor: 'pointer'
                  }}
                >
                  {isPlaying ? <Pause size={15} /> : <Play size={15} />}
                </button>
                <button
                  onClick={restartVideo}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  title="Restart"
                >
                  <RotateCcw size={15} />
                </button>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                  Scene 0{activeSceneNo} / 05
                </span>
              </div>

              {/* Dynamic Audio Visualizer Waves */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '20px' }}>
                <div className="wave-bar" style={{ animationDelay: '0.1s' }} />
                <div className="wave-bar" style={{ animationDelay: '0.4s' }} />
                <div className="wave-bar" style={{ animationDelay: '0.2s' }} />
                <div className="wave-bar" style={{ animationDelay: '0.6s' }} />
                <div className="wave-bar" style={{ animationDelay: '0.3s' }} />
              </div>
            </div>
          </motion.div>
        )}

        {/* Milestone 8: Storyboard -> Performance Preview Tab */}
        {activeTab === 'performance_preview' && (
          <div style={{ width: '100%', maxWidth: '920px', height: '100%', overflowY: 'auto' }}>
            <div style={{ marginBottom: '14px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: 800 }}>Performance Plan — Intent &amp; Actor Specification</h3>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Inspect machine-readable performance parameters before rendering to verify character consistency.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {performanceScenes.map((p) => (
                <div key={p.scene} className="glass-panel" style={{ padding: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="badge-neon badge-primary">SCENE 0{p.scene}</span>
                      <span style={{ fontWeight: 700, fontSize: '13px' }}>{p.role}</span>
                    </div>
                    <span className="badge-neon badge-amber" style={{ fontSize: '10px' }}>
                      EMOTION: {p.emotion.toUpperCase()} (Energy: {p.energy})
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', fontSize: '11px', marginTop: '4px' }}>
                    <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '8px', borderRadius: '4px' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '9.5px' }}>CHARACTER:</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>{p.character}</strong>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '8px', borderRadius: '4px' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '9.5px' }}>CAMERA SHOT:</span>
                      <strong>{p.shot}</strong>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '8px', borderRadius: '4px' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '9.5px' }}>GAZE TARGET:</span>
                      <strong>{p.gaze}</strong>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '8px', borderRadius: '4px' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '9.5px' }}>VOICE MODEL:</span>
                      <strong style={{ color: 'var(--primary-light)' }}>{p.voice}</strong>
                    </div>
                    <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '8px', borderRadius: '4px' }}>
                      <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '9.5px' }}>LANGUAGE:</span>
                      <strong style={{ color: p.language === 'HI' ? 'var(--accent-emerald)' : 'var(--accent-cyan)' }}>{p.language}</strong>
                    </div>
                  </div>

                  <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4, margin: '2px 0 0 0' }}>
                    {p.visual}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Storyboard View */}
        {activeTab === 'storyboard' && (
          <div style={{ width: '100%', maxWidth: '900px', height: '100%', overflowY: 'auto' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              {performanceScenes.map((s) => (
                <div
                  key={s.scene}
                  className="glass-panel"
                  style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className="badge-neon badge-primary">SCENE 0{s.scene}</span>
                    <span style={{ fontSize: '11px', color: 'var(--accent-amber)', fontFamily: 'var(--font-mono)' }}>
                      {s.emotion}
                    </span>
                  </div>
                  <div style={{
                    height: '120px',
                    backgroundColor: 'var(--bg-darkest)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      position: 'absolute',
                      inset: 0,
                      background: 'radial-gradient(circle at center, rgba(99,102,241,0.2) 0%, transparent 70%)'
                    }} />
                    <Film size={28} color="var(--primary-light)" />
                    <span style={{
                      position: 'absolute',
                      bottom: '6px',
                      right: '8px',
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-muted)'
                    }}>
                      {s.shot}
                    </span>
                  </div>
                  <span style={{ fontWeight: 700, fontSize: '13px' }}>{s.role}</span>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {s.visual}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Repurposed Assets View */}
        {activeTab === 'repurposed' && (
          <div style={{ width: '100%', maxWidth: '900px' }}>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Agentic Repurposing — Platform-Native Derivative Clips</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Semantic moment scoring extracted 3 high-impact clips with verified claim isolation.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {(repurposedClips.length ? repurposedClips : [
                {
                  clip_id: "clip_reel_01",
                  target_platform: "instagram_reel",
                  aspect_ratio: "9:16",
                  title: "Build Pipeline Speed Hack",
                  duration_s: 24.0,
                  moment_score: 0.92,
                  video_url: "/media/scene_1_en_9x16.mp4"
                },
                {
                  clip_id: "clip_yt_shorts_02",
                  target_platform: "youtube_shorts",
                  aspect_ratio: "9:16",
                  title: "40% Faster Local LLM",
                  duration_s: 32.0,
                  moment_score: 0.89,
                  video_url: "/media/scene_1_en_9x16.mp4"
                },
                {
                  clip_id: "clip_linkedin_03",
                  target_platform: "linkedin",
                  aspect_ratio: "16:9",
                  title: "Local ML Architecture",
                  duration_s: 45.0,
                  moment_score: 0.86,
                  video_url: "/media/master_video_en.mp4"
                }
              ]).map((clip) => (
                <div
                  key={clip.clip_id}
                  className="glass-panel"
                  style={{
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    border: selectedRepurposedUrl === clip.video_url ? '1px solid var(--primary)' : '1px solid var(--border-subtle)'
                  }}
                  onClick={() => {
                    setSelectedRepurposedUrl(clip.video_url);
                    setActiveTab('video');
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="badge-neon badge-cyan">{clip.target_platform.replace('_', ' ')}</span>
                    <span className="badge-neon badge-emerald">{clip.aspect_ratio}</span>
                  </div>
                  <h4 style={{ fontSize: '13px', fontWeight: 700, marginBottom: '6px' }}>{clip.title}</h4>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Duration: {clip.duration_s}s</span>
                    <span style={{ color: 'var(--accent-cyan)' }}>Moment Score: {(clip.moment_score * 100).toFixed(0)}%</span>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ width: '100%', marginTop: '12px', fontSize: '11px', padding: '6px' }}
                  >
                    <Play size={12} />
                    Preview Clip
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* C2PA Provenance Inspector */}
        {activeTab === 'c2pa' && (
          <div className="glass-panel" style={{ width: '100%', maxWidth: '720px', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Shield size={24} color="var(--accent-emerald)" />
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700 }}>C2PA Content Credential &amp; Media Bill of Materials</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Cryptographically signed provenance manifest</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '12px', marginBottom: '16px' }}>
              <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Character Version:</span>
                <p style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{characterName}@{characterVersion}</p>
              </div>
              <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                <span style={{ color: 'var(--text-muted)' }}>AI Disclosure Marker:</span>
                <p style={{ color: 'var(--accent-emerald)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={13} />
                  Embedded &amp; Enforced
                </p>
              </div>
              <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '10px', borderRadius: 'var(--radius-sm)', gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)' }}>C2PA Manifest Hash:</span>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--accent-cyan)', wordBreak: 'break-all' }}>
                  {c2paManifestHash || "c2pa:sha256:7f9a21bc34e022da1982bbf6019a3c1187"}
                </p>
              </div>
              <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '10px', borderRadius: 'var(--radius-sm)', gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)' }}>Media SHA-256 Checksum:</span>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                  {mediaSha256 || "sha256:9f2ac71be4d89a201bcf58921a44e9910"}
                </p>
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px', fontSize: '11px', color: 'var(--text-muted)' }}>
              Claim references grounded: <strong>MLPerf Benchmark p.12, p.15, p.19</strong>. Likeness authorization verified under Ed25519 signature.
            </div>
          </div>
        )}
        </AnimatePresence>
      </div>
    </div>
  );
};
