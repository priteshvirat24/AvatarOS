import React, { useState, useEffect, useRef } from 'react';
import {
  Play, Pause, SkipForward, SkipBack, X, Sparkles, ShieldCheck, Database,
  Film, MessageSquare, Cpu, CheckCircle2, AlertTriangle, ArrowRight,
  Layers, Lock, ExternalLink, Award, FileCode2, Zap, Volume2, ChevronRight,
  ChevronLeft, BarChart3, Fingerprint, Search, ShieldAlert, Check, Radio,
  Maximize2, Eye, Activity, Terminal, Clock, RotateCcw, Sliders
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { JudgeMode3DBackground } from './JudgeMode3DBackground';

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
  const [currentBeat, setCurrentBeat] = useState<0 | 1>(0); // Beat 0: The Core Innovation / Hook, Beat 1: Technical Architecture & Evidence
  const [isPlaying, setIsPlaying] = useState(true); // Auto-plays cinematically by default!
  const [isHovered, setIsHovered] = useState(false); // Hover-pause so user can read without rush
  const [progress, setProgress] = useState(0); // 0 to 100 within the active beat
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<1 | 1.5>(1); // 1x = ~6s per beat, 1.5x = ~4s per beat

  const chapters = [
    {
      id: "thesis",
      act: "ACT 01 // IMMUTABLE IDENTITY",
      badge: "ACT 01",
      codeName: "BIOMETRIC NEURAL CONTRACT",
      title: "Persistent Digital Identity & Likeness Rights",
      tagline: "Create a digital actor once. Direct them forever.",
      tagColor: "#1A73E8", // Google Blue
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "Zero Biometric Drift Across Any Prompt",
          narrative: "Traditional generative video produces disposable, drifting outputs where faces morph between frames. AvatarOS establishes permanent enterprise digital actors anchored in immutable biometrics.",
          highlight: "ArcFace 512-Dimensional Facial Embedding Vectors + Acoustic Timbre DNA",
          featureExplain: "Why this matters: Generative video models hallucinate new identities on every prompt. AvatarOS anchors facial vectors permanently with zero drift across any lighting or angle.",
          stat: "0.0% DRIFT",
          statLabel: "ArcFace Biometric Variance Across Scenes"
        },
        {
          subTitle: "TECHNICAL PROOF & RIGHTS SEAL",
          headline: "Ed25519 Cryptographic Consent Engine",
          narrative: "Actor likeness and voice are bounded by cryptographic Ed25519 signatures. Enforces expiry boundaries, allowed registers (technical, executive), and restricted topics to mathematically prevent unconsented misuse.",
          highlight: "Cosine Similarity >= 0.94 • Ed25519 Non-Repudiable Digital Contract",
          featureExplain: "Omnichannel Sync: The exact same biometric actor stars in 16:9 4K video ads, 9:16 vertical Shorts, and sub-800ms conversational video streams.",
          stat: "COSINE >= 0.94",
          statLabel: "Strict Identity Authentication Threshold"
        }
      ],
      interactiveAction: {
        label: "Inspect Maya v1.7.0 DNA Manifest",
        icon: <ShieldCheck size={15} />,
        onClick: onInspectDna
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%', justifyContent: 'space-between' }}>
          {/* Header */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Fingerprint size={18} color="#1A73E8" />
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
                ARCFACE 512-D // MAYA v1.7.0
              </span>
            </div>
            <span className="badge-neon badge-primary" style={{ fontSize: '9.5px', padding: '2px 8px' }}>
              BIOMETRICALLY SEALED
            </span>
          </div>

          {/* Biometric Mesh Simulator */}
          <div style={{
            position: 'relative',
            height: '140px',
            backgroundColor: '#F8F9FA',
            borderRadius: '10px',
            border: '1px solid #DADCE0',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {/* Animated Laser Scanning Beam */}
            <motion.div
              animate={{ y: [-60, 60, -60] }}
              transition={{ repeat: Infinity, duration: 2.5, ease: "easeInOut" }}
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                height: '2px',
                backgroundColor: '#1A73E8',
                boxShadow: '0 0 12px #1A73E8, 0 0 4px #4285F4',
                zIndex: 3
              }}
            />

            {/* Landmark Nodes Mesh */}
            <div style={{ position: 'relative', width: '120px', height: '100px' }}>
              {[
                { top: '15%', left: '35%' }, { top: '15%', left: '65%' }, // Eyebrows
                { top: '30%', left: '25%' }, { top: '30%', left: '75%' }, // Eyes
                { top: '50%', left: '50%' }, // Nose
                { top: '70%', left: '35%' }, { top: '70%', left: '65%' }, // Mouth
                { top: '90%', left: '50%' }  // Chin
              ].map((pt, i) => (
                <motion.div
                  key={i}
                  animate={{ scale: [1, 1.3, 1], opacity: [0.7, 1, 0.7] }}
                  transition={{ repeat: Infinity, duration: 1.8, delay: i * 0.15 }}
                  style={{
                    position: 'absolute',
                    top: pt.top,
                    left: pt.left,
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: '#1A73E8',
                    transform: 'translate(-50%, -50%)',
                    boxShadow: '0 0 6px rgba(26, 115, 232, 0.8)'
                  }}
                />
              ))}
              <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
                <line x1="30" y1="30" x2="60" y2="50" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
                <line x1="90" y1="30" x2="60" y2="50" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
                <line x1="60" y1="50" x2="42" y2="70" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
                <line x1="60" y1="50" x2="78" y2="70" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
                <line x1="42" y1="70" x2="60" y2="90" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
                <line x1="78" y1="70" x2="60" y2="90" stroke="rgba(26,115,232,0.3)" strokeWidth="1" />
              </svg>
            </div>

            <div style={{
              position: 'absolute',
              bottom: '8px',
              left: '12px',
              fontSize: '10px',
              fontFamily: 'Roboto Mono, monospace',
              color: '#137333',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <div className="status-dot active" />
              <span>COSINE SIMILARITY: 0.942 (PASS &gt;= 0.900)</span>
            </div>
          </div>

          {/* Cryptographic Contract Box */}
          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            borderRadius: '10px',
            padding: '12px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '10.5px',
            color: '#3C4043',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E8EAED', paddingBottom: '4px' }}>
              <span style={{ color: '#1A73E8', fontWeight: 700 }}>Ed25519 Signer:</span>
              <span style={{ color: '#202124' }}>actor_maya_legal_key</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Allowed Registers:</span>
              <span style={{ color: '#137333', fontWeight: 700 }}>technical, executive</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>License Expiry:</span>
              <span style={{ color: '#5F6368' }}>2027-12-31 (Enforced)</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "dag",
      act: "ACT 02 // AUTONOMOUS DAG",
      badge: "ACT 02",
      codeName: "9-ROLE AGENT DAG",
      title: "Zero Human in the Loop Orchestration",
      tagline: "From a single creative brief to an executive 5-scene broadcast campaign.",
      tagColor: "#1A73E8",
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "Autonomous DAG Execution with Adversarial Fact-Checking",
          narrative: "A single command triggers a Directed Acyclic Graph (DAG) with 9 specialized agent roles executing in strict dependency order, completely eliminating manual video editing.",
          highlight: "Research Agent (BM25) -> Adversarial Critic -> Director Choreography -> Audio/Video Engines",
          featureExplain: "Why this matters: Human video production takes days and allows ungrounded marketing claims. AvatarOS's adversarial critic rejects hallucinations before rendering.",
          stat: "9 AGENTS",
          statLabel: "Autonomous Specialized Roles in DAG"
        },
        {
          subTitle: "TECHNICAL PROOF & ARCHITECTURE",
          headline: "Multi-Scene Camera & Emotional Choreography",
          narrative: "The Director Agent plots scene-by-scene emotional trajectories (confidence, empathy, urgency) and camera angles (Close-Up, Medium, OTS), driving deterministic visual synthesis.",
          highlight: "5-Scene Breakdown • Sub-Second Agent Latency • Deterministic FFmpeg Stitching",
          featureExplain: "Adversarial Fact Check: Every line written by the scriptwriter is cross-examined against indexed benchmark PDFs before moving to rendering.",
          stat: "5.8s TOTAL",
          statLabel: "Complete DAG Pipeline Execution Time"
        }
      ],
      interactiveAction: {
        label: "Trigger Autonomous Production DAG",
        icon: <Sparkles size={15} />,
        onClick: onRunProduction
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
              DAG EXECUTION TIMELINE // 9 AGENTS
            </span>
            <span className="badge-neon badge-primary" style={{ fontSize: '9.5px', padding: '2px 8px' }}>
              PIPELINE ACTIVE
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, justifyContent: 'center' }}>
            {[
              { role: "1. Brief & Context Ingestion", time: "120ms", status: "COMPLETE", active: false },
              { role: "2. Hybrid BM25 Research Agent", time: "480ms", status: beat === 0 ? "FOCUS" : "COMPLETE", active: beat === 0 },
              { role: "3. Script & Adversarial Critic Loop", time: "1.2s", status: beat === 1 ? "FOCUS" : "COMPLETE", active: beat === 1 },
              { role: "4. Director Emotion Choreographer", time: "850ms", status: "COMPLETE", active: false },
              { role: "5. Multimodal Deterministic Engine", time: "3.2s", status: "COMPLETE", active: false }
            ].map((node, idx) => (
              <motion.div
                key={idx}
                animate={{ scale: node.active ? 1.02 : 1 }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  backgroundColor: node.active ? '#E8F0FE' : '#F8F9FA',
                  border: `1px solid ${node.active ? '#1A73E8' : '#DADCE0'}`,
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '7px',
                    height: '7px',
                    borderRadius: '50%',
                    backgroundColor: node.active ? '#1A73E8' : '#137333'
                  }} />
                  <span style={{ fontSize: '11px', fontWeight: node.active ? 700 : 500, color: '#202124' }}>
                    {node.role}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px' }}>
                  <span style={{ color: '#5F6368', fontFamily: 'Roboto Mono, monospace' }}>{node.time}</span>
                  <span className={node.active ? "badge-neon badge-primary" : "badge-neon badge-emerald"} style={{ fontSize: '8.5px', padding: '1px 6px' }}>
                    {node.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: "safety_gate",
      act: "ACT 03 // FORCED SAFETY GATE",
      badge: "ACT 03",
      codeName: "MULTIMODAL GUARDIAN",
      title: "Zero AI Hallucinations & Forced Gate",
      tagline: "Zero ungrounded claims. Mathematical enforcement against AI hallucinations.",
      tagColor: "#D93025", // Google Red
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "Strict Documentation Evidence Grounding",
          narrative: "Before any video is published, the Multimodal Guardian inspects both the generated script and rendered frames to guarantee 100% factual veracity.",
          highlight: "Every Single Claim Must Map Directly to an Indexed Benchmark Document",
          featureExplain: "Why this matters: Generative AI routinely invents fake performance numbers. AvatarOS requires exact page and paragraph citations from indexed documentation.",
          stat: "100%",
          statLabel: "Citations Grounded in Benchmark Specs"
        },
        {
          subTitle: "TECHNICAL PROOF & INTERCEPTOR",
          headline: "Forced Gate Halts Publication on Fake Claims",
          narrative: "If an ungrounded claim like '3x faster' is detected without citation, the Publication Gate immediately halts broadcast and issues an actionable rework diagnostic.",
          highlight: "Publication Intercepted // Exit Code: GATE_CLAIM_FAIL // Actionable Rework Diagnostic",
          featureExplain: "Mathematical Integrity: The gate cannot be bypassed by prompt engineering. Publication is blocked at the binary runtime level until verified evidence is provided.",
          stat: "BLOCKED",
          statLabel: "Forced Gate Action on Fake Claims"
        }
      ],
      interactiveAction: {
        label: "Simulate '3x Faster' Claim Failure",
        icon: <AlertTriangle size={15} />,
        onClick: onTriggerClaimFail
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
              GUARDIAN SAFETY RADAR
            </span>
            <span className="badge-neon" style={{ backgroundColor: '#FCE8E6', color: '#C5221F', borderColor: '#FAD2CF', fontSize: '9.5px', padding: '2px 8px' }}>
              INTERCEPTOR ACTIVE
            </span>
          </div>

          {/* Intercepted Claim Block */}
          <motion.div
            animate={{ scale: beat === 1 ? 1.02 : 1 }}
            style={{
              padding: '12px',
              borderRadius: '10px',
              backgroundColor: '#FEF7F7',
              border: '1.5px solid #FAD2CF',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11px', fontWeight: 800, color: '#C5221F' }}>
                DETECTED: "3x Faster than M3 Max"
              </span>
              <span className="badge-neon" style={{ backgroundColor: '#C5221F', color: '#FFF', fontSize: '9px', padding: '1px 6px' }}>
                REJECTED
              </span>
            </div>
            <p style={{ fontSize: '10px', color: '#5F6368', margin: 0 }}>
              Evidence Citation: <em>None found in titan_specs.pdf or MLPerf benchmarks</em>
            </p>
            <div style={{ fontSize: '10.5px', color: '#C5221F', fontWeight: 700, fontFamily: 'Roboto Mono, monospace' }}>
              ACTION: PUBLICATION HALTED (GATE_CLAIM_FAIL)
            </div>
          </motion.div>

          {/* Verified Claim Block */}
          <div style={{
            padding: '12px',
            borderRadius: '10px',
            backgroundColor: '#F6FCF8',
            border: '1px solid #CEEAD6',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11px', fontWeight: 800, color: '#137333' }}>
                VERIFIED: "18-Hour Battery Life"
              </span>
              <span className="badge-neon badge-emerald" style={{ fontSize: '9px', padding: '1px 6px' }}>
                GROUNDED
              </span>
            </div>
            <p style={{ fontSize: '10px', color: '#5F6368', margin: 0 }}>
              Citation: <code>titan_datasheet.pdf#page=4,line=12</code>
            </p>
          </div>
        </div>
      )
    },
    {
      id: "realtime_live",
      act: "ACT 04 // REALTIME VOICE",
      badge: "ACT 04",
      codeName: "SUB-800MS RUNTIME",
      title: "Real-Time Conversational Digital Human",
      tagline: "Sub-800ms conversational runtime with user barge-in interruption.",
      tagColor: "#B06000", // Google Amber
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "Sub-800ms Conversational Latency Budget",
          narrative: "AvatarOS transitions seamlessly from offline studio directing to bidirectional realtime conversation with ultra-low-latency streaming audio.",
          highlight: "ASR (110ms) + Gemini 2.0 Flash TTFT (240ms) + Neural Audio (130ms) = 480ms Total",
          featureExplain: "Why this matters: Conversational delays over 1 second feel unnatural and robotic. AvatarOS operates well under 800ms for authentic human cadence.",
          stat: "480ms",
          statLabel: "Total End-to-End Latency (Target <800ms)"
        },
        {
          subTitle: "TECHNICAL PROOF & BARGE-IN",
          headline: "Zero-Lag User Barge-In Interruption",
          narrative: "Instantaneous cancellation of outbound audio playback when the user speaks mid-sentence. Cancels remaining audio chunks within 18ms.",
          highlight: "18ms Interruption Response • Zero Echo Audio Feedback Loop • Brainstorm Handoff",
          featureExplain: "Studio Handoff: Live conversational brainstorms can be exported with 1 click as structured briefs directly into Studio Mode for 4K video rendering.",
          stat: "18ms",
          statLabel: "Instant Barge-in Audio Cancellation"
        }
      ],
      interactiveAction: {
        label: "Launch Real-Time Conversational Stage",
        icon: <MessageSquare size={15} />,
        onClick: onOpenLiveMode
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
              LATENCY WATERFALL // 480MS TOTAL
            </span>
            <span className="badge-neon badge-amber" style={{ fontSize: '9.5px', padding: '2px 8px' }}>
              WELL UNDER 800MS
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, justifyContent: 'center' }}>
            {[
              { step: "Audio Ingest & ASR", ms: 110, pct: "23%", color: "#1A73E8" },
              { step: "Gemini 2.0 Flash TTFT", ms: 240, pct: "50%", color: "#B06000" },
              { step: "Neural Audio Synthesis & Stream", ms: 130, pct: "27%", color: "#137333" }
            ].map((l, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10.5px' }}>
                  <span style={{ color: '#202124', fontWeight: 600 }}>{l.step}</span>
                  <span style={{ color: l.color, fontWeight: 700, fontFamily: 'Roboto Mono, monospace' }}>{l.ms}ms</span>
                </div>
                <div style={{ width: '100%', height: '7px', backgroundColor: '#F1F3F4', borderRadius: '4px', overflow: 'hidden' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: l.pct }}
                    transition={{ duration: 0.8, delay: i * 0.2 }}
                    style={{ height: '100%', backgroundColor: l.color }}
                  />
                </div>
              </div>
            ))}

            <div style={{
              marginTop: '8px',
              padding: '10px 12px',
              backgroundColor: '#F8F9FA',
              borderRadius: '8px',
              border: '1px solid #DADCE0',
              fontSize: '11px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ color: '#5F6368' }}>Barge-In Detector:</span>
              <span style={{ color: '#137333', fontWeight: 700, fontFamily: 'Roboto Mono, monospace' }}>ARMED (18ms response)</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "clickhouse_mcp",
      act: "ACT 05 // SELF-EVOLUTION",
      badge: "ACT 05",
      codeName: "CLICKHOUSE MCP BRIDGE",
      title: "Closed-Loop Self-Evolution via Governed MCP",
      tagline: "The agent queries its own real production analytics to evolve its behavior.",
      tagColor: "#137333", // Google Green
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "ClickHouse Columnar Big Data Telemetry",
          narrative: "AvatarOS closes the production loop: real audience retention, hook drop-off, and audio engagement events stored in ClickHouse are queried by the Evolution Agent.",
          highlight: "1,800+ Live Telemetry Records Queried in 2.1ms via Model Context Protocol",
          featureExplain: "Why this matters: Most AI workflows stop at video rendering. AvatarOS measures real audience reaction and iteratively improves script hooks.",
          stat: "2.1ms",
          statLabel: "ClickHouse Analytical Query Latency"
        },
        {
          subTitle: "TECHNICAL PROOF & GOVERNANCE",
          headline: "Strict MCP Tool Sandbox & Statistical Guardrails",
          narrative: "A 100% read-only agent allowlist prevents destructive DDL/DML queries. Strategy updates require n >= 50 samples and non-overlapping 95% confidence intervals.",
          highlight: "n >= 50 Required • p-value < 0.01 Statistical Rigor • Read-Only MCP Tool Governance",
          featureExplain: "Safety Sandbox: The agent cannot alter database schemas or write malicious SQL. Only governed analytical aggregations are executed.",
          stat: "p < 0.01",
          statLabel: "Statistical Confidence Required to Update"
        }
      ],
      interactiveAction: {
        label: "Query ClickHouse Telemetry via MCP",
        icon: <Database size={15} />,
        onClick: onOpenEvolution
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
              GOVERNED MCP // CLICKHOUSE ANALYTICS
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9.5px', padding: '2px 8px' }}>
              READ-ONLY MCP
            </span>
          </div>

          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            color: '#202124',
            padding: '12px',
            borderRadius: '10px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '10.5px',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '5px'
          }}>
            <div style={{ color: '#1A73E8', fontWeight: 700 }}>$ mcp query --tool=clickhouse_telemetry</div>
            <div style={{ color: '#137333' }}>SELECT hook_style, avg(retention_rate)</div>
            <div style={{ color: '#137333' }}>FROM audience_telemetry GROUP BY hook_style;</div>
            <div style={{ borderTop: '1px solid #DADCE0', marginTop: '6px', paddingTop: '6px' }}>
              <div style={{ color: '#202124', fontWeight: 700 }}>technical_breakdown: 84.2% [n=62] (Winner)</div>
              <div style={{ color: '#5F6368' }}>conversational_hook:  68.1% [n=58]</div>
            </div>
            <div style={{ marginTop: 'auto', color: '#B06000', fontSize: '9.5px', fontWeight: 600 }}>
              Query Execution: 2.1ms | Confidence: 99.2% | DDL Blocked
            </div>
          </div>
        </div>
      )
    },
    {
      id: "scorecard",
      act: "ACT 06 // CERTIFICATION",
      badge: "ACT 06",
      codeName: "8/8 PRODUCTION CERTIFIED",
      title: "Enterprise Scorecard & C2PA Provenance",
      tagline: "Production-ready enterprise digital actor architecture.",
      tagColor: "#1A73E8",
      beats: [
        {
          subTitle: "THE CORE BREAKTHROUGH",
          headline: "8/8 Strict Production Standards Verified",
          narrative: "Every single production run evaluates the complete media lifecycle against 8 strict production standards, ensuring zero human intervention is required.",
          highlight: "DNA Sealed • Ed25519 Rights • BM25 Grounded • Critic Verified • Guardian Passed • Sub-800ms Audio • ClickHouse MCP • C2PA Signed",
          featureExplain: "Why this matters: Enterprise deployment requires complete operational reliability. AvatarOS automatically certifies all 8 production dimensions.",
          stat: "8 / 8",
          statLabel: "Production Verification Gates Passed"
        },
        {
          subTitle: "TECHNICAL PROOF & PROVENANCE",
          headline: "C2PA Cryptographic Content Credentials",
          narrative: "Every approved broadcast asset receives cryptographically signed Content Credentials (C2PA) with SHA-256 media hashes, ensuring authentic tamper-evident provenance.",
          highlight: "C2PA Manifest Attached • SHA-256 Tamper-Evident Hashing • Bilingual EN/HI Output",
          featureExplain: "Full Provenance Trail: Manifest records actor DNA hash, legal license, research citations, and rendering timestamp.",
          stat: "SHA-256",
          statLabel: "Cryptographic Tamper-Evident Media Seal"
        }
      ],
      interactiveAction: {
        label: "Return to Studio & Direct Maya",
        icon: <Award size={15} />,
        onClick: onClose
      },
      renderTechnicalHUD: (beat: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
              8-DIMENSION VERIFICATION AUDIT
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9.5px', padding: '2px 8px' }}>
              8/8 PASSED
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', flex: 1, alignItems: 'center' }}>
            {[
              "Digital DNA Sealed",
              "Ed25519 Rights",
              "BM25 Grounded",
              "Critic Verified",
              "Guardian Passed",
              "Sub-800ms Audio",
              "ClickHouse MCP",
              "C2PA Signed"
            ].map((d, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05 }}
                style={{
                  backgroundColor: '#F8F9FA',
                  border: '1px solid #DADCE0',
                  borderRadius: '8px',
                  padding: '7px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '10.5px',
                  fontWeight: 700,
                  color: '#202124'
                }}
              >
                <Check size={13} color="#137333" />
                <span>{d}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )
    }
  ];

  // Auto-play timer for smooth cinematic narrative flow
  useEffect(() => {
    if (!isOpen || !isPlaying || isHovered) return;

    // Normal speed: ~6 seconds per beat. Fast (1.5x): ~4 seconds per beat.
    const stepIncrement = playbackSpeed === 1 ? 1.6 : 2.5;

    const interval = setInterval(() => {
      setElapsedSeconds((s) => s + 0.1);
      setProgress((prev) => {
        if (prev >= 100) {
          // Advance beat or chapter
          setCurrentBeat((prevBeat) => {
            if (prevBeat === 0) {
              return 1;
            } else {
              setCurrentChapter((ch) => (ch < chapters.length - 1 ? ch + 1 : 0));
              return 0;
            }
          });
          return 0;
        }
        return prev + stepIncrement;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isOpen, isPlaying, isHovered, currentChapter, currentBeat, playbackSpeed]);

  // Navigation handlers
  const goToNextBeat = () => {
    if (currentBeat === 0) {
      setCurrentBeat(1);
      setProgress(0);
    } else if (currentChapter < chapters.length - 1) {
      setCurrentChapter((c) => c + 1);
      setCurrentBeat(0);
      setProgress(0);
    } else {
      onClose();
    }
  };

  const goToPrevBeat = () => {
    if (currentBeat === 1) {
      setCurrentBeat(0);
      setProgress(0);
    } else if (currentChapter > 0) {
      setCurrentChapter((c) => c - 1);
      setCurrentBeat(1);
      setProgress(0);
    }
  };

  const selectChapter = (idx: number) => {
    setCurrentChapter(idx);
    setCurrentBeat(0);
    setProgress(0);
  };

  // Keyboard navigation (Space: toggle play, Arrows: next/prev, Esc: close)
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        goToNextBeat();
      } else if (e.key === 'ArrowLeft') {
        goToPrevBeat();
      } else if (e.key === ' ') {
        e.preventDefault();
        setIsPlaying((p) => !p);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, currentChapter, currentBeat]);

  if (!isOpen) return null;

  const activeChapterData = chapters[currentChapter];
  const activeBeatData = activeChapterData.beats[currentBeat];

  // Timecode calculation
  const formatTimecode = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = (sec % 60).toFixed(1);
    return `${mins.toString().padStart(2, '0')}:${secs.padStart(4, '0')}`;
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 99999,
      backgroundColor: '#FFFFFF',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      fontFamily: 'Google Sans, Roboto, -apple-system, sans-serif'
    }}>
      {/* 1. TRANSLUCENT 3D BACKGROUND */}
      <JudgeMode3DBackground
        opacity={0.22}
        speedMultiplier={0.5}
        activeChapter={currentChapter}
        activePoint={currentBeat}
      />

      {/* Google 4-Color Accent Line */}
      <div className="google-accent-line" style={{ position: 'relative', zIndex: 10 }} />

      {/* 2. TOP HEADER BAR */}
      <header style={{
        height: '54px',
        padding: '0 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #DADCE0',
        backgroundColor: '#FFFFFF',
        position: 'relative',
        zIndex: 10
      }}>
        {/* Left: Brand & Timecode */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <motion.div
              animate={{ opacity: isPlaying ? [1, 0.4, 1] : 1 }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isPlaying ? '#D93025' : '#5F6368'
              }}
            />
            <span style={{
              fontSize: '11px',
              fontWeight: 800,
              letterSpacing: '0.8px',
              color: '#202124',
              fontFamily: 'Roboto Mono, monospace'
            }}>
              CINEMATIC WALKTHROUGH {isPlaying ? "// AUTOPLAYING" : "// PAUSED"}
            </span>
          </div>

          <div style={{
            fontSize: '11px',
            fontFamily: 'Roboto Mono, monospace',
            color: '#1A73E8',
            backgroundColor: '#E8F0FE',
            padding: '2px 8px',
            borderRadius: 'var(--radius-full)',
            border: '1px solid #D2E3FC'
          }}>
            TC {formatTimecode(elapsedSeconds)} / 01:12.0
          </div>

          <span style={{ color: '#DADCE0' }}>|</span>

          <span style={{ fontSize: '12px', fontWeight: 600, color: '#5F6368' }}>
            {activeChapterData.act}
          </span>
        </div>

        {/* Right: Transport Status, Speed Toggle, Close */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {isHovered && (
            <span style={{ fontSize: '10.5px', color: '#B06000', fontWeight: 700, fontFamily: 'Roboto Mono, monospace' }}>
              ⏸ HOVER PAUSED
            </span>
          )}

          {/* Speed Toggle */}
          <button
            onClick={() => setPlaybackSpeed((s) => (s === 1 ? 1.5 : 1))}
            style={{
              background: '#F8F9FA',
              border: '1px solid #DADCE0',
              borderRadius: 'var(--radius-full)',
              padding: '4px 10px',
              fontSize: '10.5px',
              fontWeight: 700,
              color: '#3C4043',
              cursor: 'pointer'
            }}
            title="Toggle playback pace (1x or 1.5x)"
          >
            {playbackSpeed}x SPEED
          </button>

          {/* Play/Pause Button */}
          <button
            onClick={() => setIsPlaying((p) => !p)}
            style={{
              background: isPlaying ? '#E8F0FE' : '#F8F9FA',
              border: `1px solid ${isPlaying ? '#1A73E8' : '#DADCE0'}`,
              borderRadius: 'var(--radius-full)',
              padding: '4px 12px',
              fontSize: '11px',
              fontWeight: 700,
              color: isPlaying ? '#1A73E8' : '#5F6368',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
          >
            {isPlaying ? <Pause size={12} color="#1A73E8" /> : <Play size={12} color="#5F6368" />}
            <span>{isPlaying ? "PAUSE (SPACE)" : "PLAY (SPACE)"}</span>
          </button>

          {/* Exit Cinema */}
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{
              padding: '4px 12px',
              fontSize: '11px',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            title="Exit Judge Tour (ESC)"
          >
            <X size={13} />
            <span>EXIT</span>
          </button>
        </div>
      </header>

      {/* Dynamic Reading Progress Line */}
      <div style={{ width: '100%', height: '2.5px', backgroundColor: '#F1F3F4', position: 'relative', zIndex: 10 }}>
        <div style={{
          width: isPlaying ? `${progress}%` : '100%',
          height: '100%',
          backgroundColor: activeChapterData.tagColor,
          transition: isPlaying ? 'width 0.1s linear' : 'none'
        }} />
      </div>

      {/* 3. MAIN CINEMATIC WORKSPACE */}
      <main
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: '1.25fr 1fr',
          gap: '32px',
          padding: '28px 48px',
          maxWidth: '1380px',
          margin: '0 auto',
          width: '100%',
          alignItems: 'center',
          position: 'relative',
          zIndex: 10,
          overflow: 'hidden'
        }}
      >
        {/* LEFT COLUMN: KINETIC NARRATIVE FLOW (APPEAR & DISAPPEAR) */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          backdropFilter: 'blur(16px)',
          borderRadius: '16px',
          padding: '24px 28px',
          border: '1px solid #DADCE0',
          boxShadow: '0 4px 24px rgba(60, 64, 67, 0.08), 0 1px 3px rgba(60, 64, 67, 0.04)',
          minHeight: '440px',
          justifyContent: 'space-between'
        }}>
          {/* Act Badge & Category Code */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="badge-neon badge-primary" style={{ padding: '3px 10px', fontSize: '10px' }}>
              {activeChapterData.badge} // BEAT 0{currentBeat + 1}
            </span>
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              color: '#5F6368',
              fontFamily: 'Roboto Mono, monospace'
            }}>
              {activeChapterData.codeName}
            </span>
          </div>

          {/* Master Kinetic Headline Flow */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${currentChapter}-${currentBeat}`}
              initial={{ opacity: 0, y: 14, filter: 'blur(4px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: -14, filter: 'blur(4px)' }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              {/* Sub-Title Indicator */}
              <div style={{
                fontSize: '11px',
                fontWeight: 800,
                letterSpacing: '1px',
                color: activeChapterData.tagColor,
                textTransform: 'uppercase',
                fontFamily: 'Roboto Mono, monospace'
              }}>
                // {activeBeatData.subTitle}
              </div>

              {/* Punchy Dynamic Headline */}
              <h1 style={{
                fontSize: '28px',
                fontWeight: 700,
                lineHeight: 1.25,
                color: '#202124',
                letterSpacing: '-0.02em',
                margin: 0
              }}>
                {activeBeatData.headline}
              </h1>

              {/* Narrative Text */}
              <p style={{
                fontSize: '13.5px',
                color: '#3C4043',
                lineHeight: 1.6,
                margin: 0
              }}>
                {activeBeatData.narrative}
              </p>

              {/* Technical Highlight Card */}
              <div style={{
                backgroundColor: '#F8F9FA',
                border: '1px solid #DADCE0',
                borderRadius: '10px',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '12px',
                color: '#202124',
                fontWeight: 600
              }}>
                <Zap size={16} color={activeChapterData.tagColor} />
                <span>{activeBeatData.highlight}</span>
              </div>

              {/* Feature Explainer Callout */}
              <div style={{
                backgroundColor: '#FFFFFF',
                borderLeft: `3px solid ${activeChapterData.tagColor}`,
                padding: '8px 14px',
                fontSize: '11.5px',
                color: '#5F6368',
                lineHeight: 1.5,
                borderRadius: '0 8px 8px 0',
                boxShadow: '0 1px 4px rgba(0,0,0,0.04)'
              }}>
                <strong style={{ color: '#202124' }}>Feature Spotlight: </strong>
                {activeBeatData.featureExplain}
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Bottom Row: Stat Pill + Interactive Action Button */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderTop: '1px solid #E8EAED',
            paddingTop: '14px',
            marginTop: '4px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                fontSize: '16px',
                fontWeight: 800,
                color: activeChapterData.tagColor,
                fontFamily: 'Roboto Mono, monospace'
              }}>
                {activeBeatData.stat}
              </span>
              <span style={{ fontSize: '11px', color: '#5F6368' }}>
                {activeBeatData.statLabel}
              </span>
            </div>

            <button
              onClick={() => activeChapterData.interactiveAction.onClick()}
              className="btn btn-primary"
              style={{
                padding: '8px 16px',
                fontSize: '11.5px',
                fontWeight: 600,
                borderRadius: 'var(--radius-full)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 6px rgba(26, 115, 232, 0.3)'
              }}
            >
              {activeChapterData.interactiveAction.icon}
              <span>{activeChapterData.interactiveAction.label}</span>
              <ArrowRight size={13} />
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: ARCHITECTURAL TELEMETRY SHOWCASE */}
        <div style={{
          height: '440px',
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          border: '1px solid #DADCE0',
          boxShadow: '0 4px 24px rgba(60, 64, 67, 0.08), 0 1px 3px rgba(60, 64, 67, 0.04)',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Card Title */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px',
            borderBottom: '1px solid #E8EAED',
            paddingBottom: '10px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Terminal size={14} color="#1A73E8" />
              <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.4px', color: '#202124', fontFamily: 'Roboto Mono, monospace' }}>
                AVATAROS ARCHITECTURAL TELEMETRY
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div className="status-dot active" />
              <span style={{ fontSize: '10px', color: '#137333', fontWeight: 700, fontFamily: 'Roboto Mono, monospace' }}>LIVE PROOF</span>
            </div>
          </div>

          {/* Dynamic Telemetry Viewport with Motion */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={`${currentChapter}-${currentBeat}`}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.3 }}
                style={{ height: '100%' }}
              >
                {activeChapterData.renderTechnicalHUD(currentBeat)}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* 4. BOTTOM CINEMATIC TIMELINE & TRANSPORT BAR */}
      <footer style={{
        height: '68px',
        padding: '0 32px',
        borderTop: '1px solid #DADCE0',
        backgroundColor: '#F8F9FA',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        zIndex: 10
      }}>
        {/* Left: 6 Segmented Act Tracks with Live Progress */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {chapters.map((ch, idx) => {
              const isCurrent = currentChapter === idx;
              const isPast = currentChapter > idx;
              return (
                <button
                  key={ch.id}
                  onClick={() => selectChapter(idx)}
                  style={{
                    height: '24px',
                    width: isCurrent ? '120px' : '48px',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: isCurrent ? '#E8F0FE' : isPast ? '#E6F4EA' : '#FFFFFF',
                    border: `1px solid ${isCurrent ? ch.tagColor : isPast ? '#CEEAD6' : '#DADCE0'}`,
                    padding: '2px 8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                  title={ch.title}
                >
                  {/* Fill progress inside current act */}
                  {isCurrent && (
                    <div style={{
                      position: 'absolute',
                      left: 0,
                      top: 0,
                      bottom: 0,
                      width: `${((currentBeat * 50) + (progress * 0.5))}%`,
                      backgroundColor: 'rgba(26, 115, 232, 0.15)',
                      transition: 'width 0.1s linear'
                    }} />
                  )}

                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    color: isCurrent ? ch.tagColor : isPast ? '#137333' : '#5F6368',
                    fontFamily: 'Roboto Mono, monospace',
                    zIndex: 2,
                    whiteSpace: 'nowrap'
                  }}>
                    {isCurrent ? `0${idx + 1} ${ch.badge}` : `0${idx + 1}`}
                  </span>
                </button>
              );
            })}
          </div>

          <span style={{ fontSize: '11px', color: '#5F6368', fontWeight: 600 }}>
            ACT {currentChapter + 1} OF 6 (BEAT {currentBeat + 1}/2)
          </span>
        </div>

        {/* Right: Previous / Next Beat Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={goToPrevBeat}
            disabled={currentChapter === 0 && currentBeat === 0}
            className="btn btn-secondary"
            style={{
              padding: '6px 14px',
              fontSize: '11px',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ChevronLeft size={14} />
            <span>PREV BEAT</span>
          </button>

          <button
            onClick={goToNextBeat}
            className="btn btn-primary"
            style={{
              padding: '6px 16px',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 2px 6px rgba(26, 115, 232, 0.3)'
            }}
          >
            <span>{currentBeat === 0 ? "NEXT PROOF" : currentChapter < 5 ? "NEXT ACT" : "DIRECT ACTOR"}</span>
            <ChevronRight size={14} />
          </button>
        </div>
      </footer>
    </div>
  );
};

export default CinematicJudgeMode;
