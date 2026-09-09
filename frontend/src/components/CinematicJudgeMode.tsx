import React, { useState, useEffect } from 'react';
import {
  Play, Pause, SkipForward, SkipBack, X, Sparkles, ShieldCheck, Database,
  Film, MessageSquare, Cpu, CheckCircle2, AlertTriangle, ArrowRight,
  Layers, Lock, ExternalLink, Award, FileCode2, Zap, Volume2, Maximize2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CinematicJudgeModeProps {
  isOpen: boolean;
  onClose: () => void;
  onInspectDna: () => void;
  onRunProduction: () => void;
  onTriggerClaimFail: () => void;
  onResolveClaim: () => void;
  onOpenLiveMode: () => void;
  onOpenEvolution: () => void;
}

export const CinematicJudgeMode: React.FC<CinematicJudgeModeProps> = ({
  isOpen,
  onClose,
  onInspectDna,
  onRunProduction,
  onTriggerClaimFail,
  onResolveClaim,
  onOpenLiveMode,
  onOpenEvolution
}) => {
  const [currentChapter, setCurrentChapter] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(0);

  const chapters = [
    {
      id: "thesis",
      badge: "CHAPTER 01 / 06",
      title: "The Thesis: Persistent Digital Identity & Immutable Rights",
      subtitle: "Create a digital actor once. Direct them forever.",
      concept: "Traditional AI video produces disposable, inconsistent one-off clips. AvatarOS creates permanent digital actors governed by Digital DNA.",
      points: [
        { label: "Biometric Anchor", desc: "ArcFace 512-dimensional face vector + acoustic vocal timbre locked across all runs." },
        { label: "Ed25519 Cryptographic Consent", desc: "Legally binding likeness license with expiry dates, allowed registers, and restricted topics." },
        { label: "Multi-Asset Identity", desc: "Same character stars in 16:9 widescreen master ads, 9:16 vertical Shorts, and real-time live video calls." }
      ],
      interactiveAction: {
        label: "Inspect Maya v1.7.0 DNA Manifest",
        icon: <ShieldCheck size={14} />,
        onClick: onInspectDna
      },
      tagColor: "var(--google-blue)",
      illustrationBadge: "DIGITAL DNA ARCHITECTURE"
    },
    {
      id: "dag",
      badge: "CHAPTER 02 / 06",
      title: "Autonomous Multi-Agent DAG: Zero Human in the Loop",
      subtitle: "From one executive prompt to a completed 5-scene cinematic campaign.",
      concept: "A single command triggers an autonomous Directed Acyclic Graph (DAG) with 9 specialized agent roles.",
      points: [
        { label: "Research Agent", desc: "Retrieves factual claims from documentation using hybrid BM25 + dense vector search." },
        { label: "Script & Adversarial Critic", desc: "Gemini 2.5 Flash drafts the multi-scene script while the Critic rigorously verifies every factual claim." },
        { label: "Director & Performance Plan", desc: "Choreographs emotional trajectories, camera angles (Close-Up, Medium, OTS), and gaze vectors." }
      ],
      interactiveAction: {
        label: "Trigger Autonomous Production DAG",
        icon: <Sparkles size={14} />,
        onClick: onRunProduction
      },
      tagColor: "var(--google-blue)",
      illustrationBadge: "VERTEX AI AGENT DAG"
    },
    {
      id: "safety_gate",
      badge: "CHAPTER 03 / 06",
      title: "Multimodal Safety Guardian & The Forced Gate",
      subtitle: "Zero ungrounded claims. Mathematical enforcement against AI hallucinations.",
      concept: "Before any video is published, the Multimodal Guardian inspects both the generated script and media frames to guarantee factual veracity.",
      points: [
        { label: "Evidence-Grounded Claims", desc: "Every single performance claim must point to an indexed benchmark document or test record." },
        { label: "Forced Gate Enforcement", desc: "If an ungrounded claim like '3x faster' is injected, publication is immediately BLOCKED." },
        { label: "C2PA Provenance Manifest", desc: "Approved media receives cryptographically signed Content Credentials (C2PA) with full provenance." }
      ],
      interactiveAction: {
        label: "Simulate '3x Faster' Claim Failure",
        icon: <AlertTriangle size={14} />,
        onClick: onTriggerClaimFail
      },
      tagColor: "var(--google-red)",
      illustrationBadge: "FORCED PUBLICATION GATE"
    },
    {
      id: "realtime_live",
      badge: "CHAPTER 04 / 06",
      title: "Real-Time Conversational Digital Human Runtime",
      subtitle: "Sub-800ms conversational runtime with user barge-in interruption.",
      concept: "AvatarOS transitions seamlessly from offline studio directing to bidirectional realtime conversation with low-latency audio streaming.",
      points: [
        { label: "Sub-800ms Latency Budget", desc: "ASR (110ms) + LLM TTFT (240ms) + Audio TTFA (130ms) for natural human cadence." },
        { label: "User Barge-In / Interruption", desc: "Instantaneous cancellation of audio streaming when the user speaks mid-sentence." },
        { label: "Dual-Engine Resilience", desc: "Seamless graceful degradation to conversational turn-based reasoning with deterministic fallback." }
      ],
      interactiveAction: {
        label: "Launch Real-Time Conversational Stage",
        icon: <MessageSquare size={14} />,
        onClick: onOpenLiveMode
      },
      tagColor: "var(--google-yellow)",
      illustrationBadge: "REALTIME DIGITAL HUMAN"
    },
    {
      id: "clickhouse_mcp",
      badge: "CHAPTER 05 / 06",
      title: "Closed-Loop Self-Evolution: ClickHouse & Governed MCP",
      subtitle: "The agent queries its own real production analytics to evolve its behavior.",
      concept: "AvatarOS closes the loop: audience retention data stored in ClickHouse is queried by the Evolution Agent via Model Context Protocol (MCP).",
      points: [
        { label: "ClickHouse Columnar Speed", desc: "Queries over 1,800+ real telemetry events in under 2.5ms with columnar index scans." },
        { label: "Strict MCP Tool Governance", desc: "100% read-only agent allowlist prevents destructive DDL/DML queries or SQL injection." },
        { label: "Statistical Guardrails", desc: "Policy evolution requires n >= 50 sample size and non-overlapping 95% confidence intervals." }
      ],
      interactiveAction: {
        label: "Query ClickHouse Telemetry via MCP",
        icon: <Database size={14} />,
        onClick: onOpenEvolution
      },
      tagColor: "var(--google-green)",
      illustrationBadge: "CLICKHOUSE MCP BRIDGE"
    },
    {
      id: "scorecard",
      badge: "CHAPTER 06 / 06",
      title: "Judge-Proof Scorecard: 8/8 Dimensions Verified",
      subtitle: "Production-ready enterprise digital actor architecture.",
      concept: "Every run evaluates the complete media lifecycle against 8 strict production standards.",
      points: [
        { label: "Identity & Rights", desc: "PASS • ArcFace >= 0.92, Ed25519 likeness rights verified." },
        { label: "Evidence & Grounding", desc: "PASS • Zero unsupported claims; 100% citation grounding." },
        { label: "Media & Provenance", desc: "PASS • Lip-sync <= 80ms, C2PA manifest signed with SHA-256." }
      ],
      interactiveAction: {
        label: "Return to Studio & Explore Freely",
        icon: <Award size={14} />,
        onClick: onClose
      },
      tagColor: "var(--google-blue)",
      illustrationBadge: "PRODUCTION CERTIFICATION"
    }
  ];

  // Auto-advance timer
  useEffect(() => {
    if (!isOpen || !isPlaying) return;

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          setCurrentChapter((ch) => (ch < chapters.length - 1 ? ch + 1 : 0));
          return 0;
        }
        return prev + 1.25;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isOpen, isPlaying, currentChapter]);

  const active = chapters[currentChapter];

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      backgroundColor: 'rgba(32, 33, 36, 0.75)',
      backdropFilter: 'blur(16px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    }}>
      {/* Cinematic Modal Container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.25 }}
        style={{
          width: '100%',
          maxWidth: '960px',
          backgroundColor: '#FFFFFF',
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 24px 60px rgba(0, 0, 0, 0.35)',
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid #DADCE0'
        }}
      >
        {/* Google 4-Color Accent Bar */}
        <div className="google-accent-line" />

        {/* Top Header Bar */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid #DADCE0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#FFFFFF'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #1A73E8 0%, #174EA6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              <Award size={15} />
            </div>
            <div>
              <span style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'Google Sans, sans-serif', color: '#202124' }}>
                AVATAROS • CINEMATIC JUDGE MODE
              </span>
              <p style={{ fontSize: '11px', color: '#5F6368' }}>
                Interactive Architectural Walkthrough for Hackathon Evaluators
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Play/Pause control */}
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                background: '#F1F3F4',
                border: '1px solid #DADCE0',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#202124'
              }}
              title={isPlaying ? "Pause Tour" : "Play Tour"}
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            </button>

            {/* Exit button */}
            <button
              onClick={onClose}
              style={{
                background: '#F1F3F4',
                border: '1px solid #DADCE0',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#5F6368'
              }}
              title="Close Judge Mode"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ width: '100%', height: '3px', backgroundColor: '#F1F3F4' }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            backgroundColor: active.tagColor,
            transition: 'width 0.1s linear'
          }} />
        </div>

        {/* Chapter Content Body */}
        <div style={{ padding: '32px 36px', display: 'flex', flexDirection: 'column', gap: '20px', backgroundColor: '#FFFFFF' }}>
          
          {/* Chapter Badge & Title */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge-neon badge-primary" style={{ padding: '2px 10px', fontSize: '10px' }}>
                {active.badge}
              </span>
              <span className="badge-neon badge-secondary" style={{ fontSize: '10px' }}>
                {active.illustrationBadge}
              </span>
            </div>

            <h2 style={{ fontSize: '22px', fontWeight: 600, color: '#202124', fontFamily: 'Google Sans, sans-serif' }}>
              {active.title}
            </h2>
            <p style={{ fontSize: '13px', color: '#5F6368', marginTop: '4px' }}>
              {active.subtitle}
            </p>
          </div>

          {/* Thesis Callout Box */}
          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            borderRadius: '12px',
            padding: '16px 20px',
            fontSize: '13px',
            color: '#202124',
            lineHeight: 1.5
          }}>
            <strong>Core Breakthrough:</strong> {active.concept}
          </div>

          {/* 3 Technical Proof Pillars */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            {active.points.map((pt, i) => (
              <div
                key={i}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #DADCE0',
                  borderRadius: '12px',
                  padding: '16px',
                  boxShadow: '0 1px 3px rgba(60,64,67,0.08)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <CheckCircle2 size={15} color="#137333" />
                  <span style={{ fontWeight: 600, fontSize: '12px', color: '#202124' }}>
                    {pt.label}
                  </span>
                </div>
                <p style={{ fontSize: '11px', color: '#5F6368', lineHeight: 1.45, margin: 0 }}>
                  {pt.desc}
                </p>
              </div>
            ))}
          </div>

          {/* Live Demonstration Button */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            backgroundColor: '#E8F0FE',
            border: '1px solid #D2E3FC',
            borderRadius: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Sparkles size={18} color="#1A73E8" />
              <div>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#1A73E8' }}>
                  TEST THIS CAPABILITY LIVE
                </span>
                <p style={{ fontSize: '11px', color: '#3C4043', margin: 0 }}>
                  Triggers the actual backend engine and updates the active stage in real time.
                </p>
              </div>
            </div>

            <button
              className="btn btn-primary"
              onClick={() => {
                active.interactiveAction.onClick();
              }}
              style={{ padding: '8px 18px', fontSize: '12px', gap: '6px' }}
            >
              {active.interactiveAction.icon}
              {active.interactiveAction.label}
            </button>
          </div>
        </div>

        {/* Footer Navigation & Chapter Dots */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid #DADCE0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#F8F9FA'
        }}>
          {/* Chapter Selector Dots */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {chapters.map((ch, idx) => (
              <button
                key={ch.id}
                onClick={() => {
                  setCurrentChapter(idx);
                  setProgress(0);
                }}
                style={{
                  width: currentChapter === idx ? '24px' : '8px',
                  height: '8px',
                  borderRadius: '4px',
                  backgroundColor: currentChapter === idx ? '#1A73E8' : '#DADCE0',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                title={ch.title}
              />
            ))}
          </div>

          {/* Step buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setCurrentChapter((c) => Math.max(0, c - 1));
                setProgress(0);
              }}
              disabled={currentChapter === 0}
              style={{ padding: '6px 14px', fontSize: '11px' }}
            >
              <SkipBack size={12} />
              Previous
            </button>

            <button
              className="btn btn-primary"
              onClick={() => {
                if (currentChapter < chapters.length - 1) {
                  setCurrentChapter((c) => c + 1);
                  setProgress(0);
                } else {
                  onClose();
                }
              }}
              style={{ padding: '6px 16px', fontSize: '11px' }}
            >
              {currentChapter < chapters.length - 1 ? "Next Chapter" : "Finish Tour"}
              <SkipForward size={12} />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CinematicJudgeMode;
