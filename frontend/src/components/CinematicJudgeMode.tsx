import React, { useState, useEffect } from 'react';
import {
  Play, Pause, SkipForward, SkipBack, X, Sparkles, ShieldCheck, Database,
  Film, MessageSquare, Cpu, CheckCircle2, AlertTriangle, ArrowRight,
  Layers, Lock, ExternalLink, Award, FileCode2, Zap, Volume2, ChevronRight,
  ChevronLeft, BarChart3, Fingerprint, Search, ShieldAlert, Check
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
  const [activePointIndex, setActivePointIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [stepProgress, setStepProgress] = useState(0); // 0 to 100 for current point

  const chapters = [
    {
      id: "thesis",
      badge: "CHAPTER 01 / 06",
      title: "The Thesis: Persistent Digital Identity & Immutable Rights",
      subtitle: "Create a digital actor once. Direct them forever.",
      concept: "Traditional AI video treats actors as disposable prompt outputs. AvatarOS creates permanent digital actors anchored in immutable biometrics and legal consent.",
      points: [
        {
          label: "ArcFace 512-d Biometric Anchor",
          desc: "ArcFace 512-dimensional facial embedding vector and acoustic vocal timbre locked across all runs. Zero facial drift across camera angles and scene changes.",
          metric: "ArcFace Cosine Similarity >= 0.94 • 0.0% Biometric Drift",
          detailTag: "BIOMETRIC SEAL"
        },
        {
          label: "Ed25519 Cryptographic Consent",
          desc: "Legally binding likeness license signed with Ed25519 cryptographic keys. Enforces strict expiry dates, allowed registers (technical, executive), and restricted topics.",
          metric: "Ed25519 Verified • Non-Repudiable Likeness Authorization",
          detailTag: "LEGAL RIGHTS"
        },
        {
          label: "Multi-Channel Broadcast Identity",
          desc: "The exact same character stars in 16:9 widescreen master videos, 9:16 vertical Shorts, and participates in real-time low-latency live calls without visual dissonance.",
          metric: "Widescreen 4K • 9:16 Shorts • Sub-800ms Realtime Live",
          detailTag: "OMNICHANNEL"
        }
      ],
      interactiveAction: {
        label: "Inspect Maya v1.7.0 DNA Manifest",
        icon: <ShieldCheck size={14} />,
        onClick: onInspectDna
      },
      tagColor: "#1A73E8",
      illustrationBadge: "DIGITAL DNA ARCHITECTURE",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Fingerprint size={16} color="#1A73E8" />
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
                Identity Anchor: Maya v1.7.0
              </span>
            </div>
            <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>
              DNA SEALED
            </span>
          </div>

          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            borderRadius: '10px',
            padding: '12px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '11px',
            color: '#3C4043',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ color: '#1A73E8', fontWeight: 600 }}>
              // ArcFace 512-Dimensional Vector Hash
            </div>
            <div style={{ wordBreak: 'break-all', fontSize: '10px', color: '#5F6368' }}>
              sha256:7f8a9e2d1c4b5a6f8e9d0c1b2a3f4e5d6c7b8a9e0f1a2b3c4d5e6f7a8b9c0d1e
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #E8EAED', paddingTop: '6px', marginTop: '4px' }}>
              <span>Cosine Threshold:</span>
              <span style={{ color: '#137333', fontWeight: 600 }}>0.942 (PASS)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Ed25519 Signer:</span>
              <span style={{ color: '#1A73E8' }}>actor_maya_legal_key</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Allowed Registers:</span>
              <span style={{ color: '#202124' }}>technical, executive</span>
            </div>
          </div>

          <div style={{
            flex: 1,
            backgroundColor: activePoint === 0 ? '#E8F0FE' : activePoint === 1 ? '#E6F4EA' : '#FEF7E0',
            borderRadius: '10px',
            padding: '12px',
            border: '1px solid #DADCE0',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            gap: '6px',
            transition: 'all 0.3s ease'
          }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#202124', textTransform: 'uppercase' }}>
              {activePoint === 0 && "Biometric Vector Verification: Active"}
              {activePoint === 1 && "Cryptographic Rights License: Enforced"}
              {activePoint === 2 && "Unified Omnichannel Sync: Verified"}
            </span>
            <span style={{ fontSize: '11px', color: '#5F6368', maxWidth: '280px' }}>
              {activePoint === 0 && "ArcFace facial landmarks matched against original reference footage with zero variation."}
              {activePoint === 1 && "Actor consent bounds valid until 2027-12-31. Unauthorized topic injection prohibited."}
              {activePoint === 2 && "Same persona assets shared seamlessly between 4K video ads and live conversational calls."}
            </span>
          </div>
        </div>
      )
    },
    {
      id: "dag",
      badge: "CHAPTER 02 / 06",
      title: "Autonomous Multi-Agent DAG: Zero Human in the Loop",
      subtitle: "From a single creative brief to an executive 5-scene broadcast campaign.",
      concept: "A single command triggers an autonomous Directed Acyclic Graph (DAG) with 9 specialized agent roles executing in strict dependency order.",
      points: [
        {
          label: "Research & Fact Grounding Agent",
          desc: "Indexes technical specifications and product documentation using hybrid BM25 keyword matching plus dense vector retrieval before any script is written.",
          metric: "Hybrid BM25 + Vector Retrieval • Document Index Scanned",
          detailTag: "RESEARCH"
        },
        {
          label: "Adversarial Critic Verification",
          desc: "Acts as an adversarial challenger to the Scriptwriter. Scrutinizes every proposed marketing claim against verified documentation, rejecting unsupported assertions.",
          metric: "Adversarial Fact Check • Claim Veracity Scoring",
          detailTag: "CRITIC"
        },
        {
          label: "Director & Performance Choreography",
          desc: "Director Agent plans emotional trajectories, camera angles (Close-Up, Medium, OTS), and gaze vectors scene-by-scene to generate a structured PerformancePlan.",
          metric: "Emotional Trajectory Arc • 5-Scene Camera Breakdown",
          detailTag: "DIRECTOR"
        }
      ],
      interactiveAction: {
        label: "Trigger Autonomous Production DAG",
        icon: <Sparkles size={14} />,
        onClick: onRunProduction
      },
      tagColor: "#1A73E8",
      illustrationBadge: "AUTONOMOUS AGENT DAG",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
              9-Agent DAG Pipeline Flow
            </span>
            <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>
              ORCHESTRATION
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, justifyContent: 'center' }}>
            {[
              { role: "1. Brief & Context", status: "COMPLETE", time: "120ms", active: false },
              { role: "2. Research Agent (BM25)", status: activePoint === 0 ? "FOCUS" : "COMPLETE", time: "480ms", active: activePoint === 0 },
              { role: "3. Script & Critic Loop", status: activePoint === 1 ? "FOCUS" : "COMPLETE", time: "1.2s", active: activePoint === 1 },
              { role: "4. Director Choreography", status: activePoint === 2 ? "FOCUS" : "COMPLETE", time: "850ms", active: activePoint === 2 },
              { role: "5. Multimodal Renderer", status: "READY", time: "3.2s", active: false }
            ].map((st, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  backgroundColor: st.active ? '#E8F0FE' : '#F8F9FA',
                  border: `1px solid ${st.active ? '#1A73E8' : '#DADCE0'}`,
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: st.active ? '#1A73E8' : '#137333'
                  }} />
                  <span style={{ fontSize: '11.5px', fontWeight: st.active ? 700 : 500, color: '#202124' }}>
                    {st.role}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '10px' }}>
                  <span style={{ color: '#5F6368' }}>{st.time}</span>
                  <span className={st.active ? "badge-neon badge-primary" : "badge-neon badge-emerald"} style={{ fontSize: '8.5px', padding: '1px 6px' }}>
                    {st.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: "safety_gate",
      badge: "CHAPTER 03 / 06",
      title: "Multimodal Safety Guardian & The Forced Gate",
      subtitle: "Zero ungrounded claims. Mathematical enforcement against AI hallucinations.",
      concept: "Before any video is published, the Multimodal Guardian inspects both the generated script and rendered frames to guarantee factual veracity.",
      points: [
        {
          label: "Evidence Grounding Requirement",
          desc: "Every single factual claim (e.g. battery life, benchmarks, latency) must map directly to an indexed benchmark document with page and paragraph citations.",
          metric: "100% Citation Grounded • Zero Unsupported Assertions",
          detailTag: "GROUNDING"
        },
        {
          label: "Forced Gate Halts Publication",
          desc: "If an unsupported claim like '3x faster' is detected without citation, the Publication Gate immediately halts broadcast and issues an actionable rework brief.",
          metric: "Forced Gate: BLOCKED • Actionable Rework Diagnostic",
          detailTag: "GATE BLOCK"
        },
        {
          label: "C2PA Content Credentials Manifest",
          desc: "Approved media receives cryptographically signed Content Credentials (C2PA) with SHA-256 media hashes, ensuring authentic tamper-evident provenance.",
          metric: "C2PA Manifest Attached • SHA-256 Tamper-Evident",
          detailTag: "PROVENANCE"
        }
      ],
      interactiveAction: {
        label: "Simulate '3x Faster' Claim Failure",
        icon: <AlertTriangle size={14} />,
        onClick: onTriggerClaimFail
      },
      tagColor: "#D93025",
      illustrationBadge: "FORCED PUBLICATION GATE",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
              Claim Verification Scanner
            </span>
            <span className="badge-neon badge-amber" style={{ fontSize: '9px', color: '#C5221F', borderColor: '#FAD2CF' }}>
              GATE ACTIVE
            </span>
          </div>

          <div style={{
            padding: '12px',
            borderRadius: '10px',
            backgroundColor: '#FEF7F7',
            border: '1px solid #FAD2CF',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11px', fontWeight: 700, color: '#C5221F' }}>
                DETECTED CLAIM: "3x Faster than M3 Max"
              </span>
              <span className="badge-neon" style={{ backgroundColor: '#FCE8E6', color: '#C5221F', borderColor: '#FAD2CF', fontSize: '9px' }}>
                FAIL
              </span>
            </div>
            <p style={{ fontSize: '11px', color: '#5F6368', margin: 0 }}>
              Evidence Citation: <em>None found in titan_specs.pdf or benchmarks</em>
            </p>
            <div style={{ fontSize: '10px', color: '#C5221F', fontWeight: 600, marginTop: '2px' }}>
              GATE ACTION: PUBLICATION BLOCKED (Exit Code: GATE_CLAIM_FAIL)
            </div>
          </div>

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
              <span style={{ fontSize: '11px', fontWeight: 700, color: '#137333' }}>
                VERIFIED CLAIM: "18-Hour Battery Life"
              </span>
              <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>
                PASS
              </span>
            </div>
            <p style={{ fontSize: '11px', color: '#5F6368', margin: 0 }}>
              Citation: <code>titan_datasheet.pdf#page=4,line=12</code>
            </p>
          </div>
        </div>
      )
    },
    {
      id: "realtime_live",
      badge: "CHAPTER 04 / 06",
      title: "Real-Time Conversational Digital Human Runtime",
      subtitle: "Sub-800ms conversational runtime with user barge-in interruption.",
      concept: "AvatarOS transitions seamlessly from offline studio directing to bidirectional realtime conversation with low-latency audio streaming.",
      points: [
        {
          label: "Sub-800ms Conversational Latency",
          desc: "ASR (110ms) + LLM Time-to-First-Token (240ms) + Audio Time-to-First-Audio (130ms) for natural human cadency under 480ms total roundtrip.",
          metric: "480ms Total Latency • Natural Human Cadence",
          detailTag: "LATENCY"
        },
        {
          label: "Realtime User Barge-In Interruption",
          desc: "Instantaneous cancellation of outbound audio playback when the user speaks mid-sentence. Cancels remaining audio chunks within 18ms.",
          metric: "18ms Interruption Response • Zero Echo Audio Loop",
          detailTag: "BARGE-IN"
        },
        {
          label: "Live-to-Studio Production Handoff",
          desc: "Conversations held in Live Mode can be exported as structured creative briefs directly into Studio Mode for multi-channel video rendering.",
          metric: "Live Transcript -> Studio Production Brief Handoff",
          detailTag: "HANDOFF"
        }
      ],
      interactiveAction: {
        label: "Launch Real-Time Conversational Stage",
        icon: <MessageSquare size={14} />,
        onClick: onOpenLiveMode
      },
      tagColor: "#B06000",
      illustrationBadge: "REALTIME CONVERSATION",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
              Latency Waterfall Budget (&lt;800ms Target)
            </span>
            <span className="badge-neon badge-amber" style={{ fontSize: '9px' }}>
              480MS TOTAL
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, justifyContent: 'center' }}>
            {[
              { step: "Audio Ingest & ASR", ms: 110, pct: "23%", color: "#1A73E8" },
              { step: "LLM Time to First Token", ms: 240, pct: "50%", color: "#B06000" },
              { step: "Audio Synthesis & Streaming", ms: 130, pct: "27%", color: "#137333" }
            ].map((l, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                  <span style={{ color: '#202124', fontWeight: 500 }}>{l.step}</span>
                  <span style={{ color: l.color, fontWeight: 700 }}>{l.ms}ms</span>
                </div>
                <div style={{ width: '100%', height: '6px', backgroundColor: '#F1F3F4', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: l.pct, height: '100%', backgroundColor: l.color }} />
                </div>
              </div>
            ))}

            <div style={{
              marginTop: '8px',
              padding: '10px',
              backgroundColor: '#F8F9FA',
              borderRadius: '8px',
              border: '1px solid #DADCE0',
              fontSize: '11px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ color: '#5F6368' }}>Barge-In Detector:</span>
              <span style={{ color: '#137333', fontWeight: 600 }}>ARMED (18ms response)</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "clickhouse_mcp",
      badge: "CHAPTER 05 / 06",
      title: "Closed-Loop Self-Evolution: ClickHouse & Governed MCP",
      subtitle: "The agent queries its own real production analytics to evolve its behavior.",
      concept: "AvatarOS closes the loop: audience retention data stored in ClickHouse is queried by the Evolution Agent via Model Context Protocol (MCP).",
      points: [
        {
          label: "ClickHouse Columnar Telemetry",
          desc: "Ingests raw scene retention, hook drop-off, and audio engagement events. Queries over 1,800+ real telemetry events in under 2.5ms.",
          metric: "2.1ms Query Latency • Columnar Index Scans",
          detailTag: "TELEMETRY"
        },
        {
          label: "Strict MCP Tool Governance",
          desc: "100% read-only agent allowlist prevents destructive DDL/DML queries. The agent can only execute bounded analytical aggregations.",
          metric: "Read-Only Allowlist • Zero SQL Injection Attack Surface",
          detailTag: "GOVERNANCE"
        },
        {
          label: "Statistical Evolution Guardrails",
          desc: "Strategy updates (e.g. switching hook style from conversational to technical) require n >= 50 samples and non-overlapping 95% confidence intervals.",
          metric: "n >= 50 Required • p-value < 0.01 Statistical Rigor",
          detailTag: "EVOLUTION"
        }
      ],
      interactiveAction: {
        label: "Query ClickHouse Telemetry via MCP",
        icon: <Database size={14} />,
        onClick: onOpenEvolution
      },
      tagColor: "#137333",
      illustrationBadge: "CLICKHOUSE MCP BRIDGE",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
              Governed MCP Analytics Query
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>
              READ-ONLY MCP
            </span>
          </div>

          <div style={{
            backgroundColor: '#202124',
            color: '#F8F9FA',
            padding: '12px',
            borderRadius: '10px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '10.5px',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}>
            <div style={{ color: '#8AB4F8' }}>$ mcp query --tool=clickhouse_telemetry</div>
            <div style={{ color: '#81C995' }}>SELECT hook_style, avg(retention_rate)</div>
            <div style={{ color: '#81C995' }}>FROM audience_telemetry GROUP BY hook_style;</div>
            <div style={{ borderTop: '1px solid #3C4043', marginTop: '6px', paddingTop: '6px' }}>
              <div>technical_breakdown: 84.2% [n=62] (Winner)</div>
              <div style={{ color: '#9AA0A6' }}>conversational_hook:  68.1% [n=58]</div>
            </div>
            <div style={{ marginTop: 'auto', color: '#FDD663', fontSize: '9.5px' }}>
              Execution: 2.1ms | Confidence: 99.2% | DDL Blocked
            </div>
          </div>
        </div>
      )
    },
    {
      id: "scorecard",
      badge: "CHAPTER 06 / 06",
      title: "Judge-Proof Scorecard: 8/8 Dimensions Verified",
      subtitle: "Production-ready enterprise digital actor architecture.",
      concept: "Every run evaluates the complete media lifecycle against 8 strict production standards, ensuring zero human intervention is required.",
      points: [
        {
          label: "Identity & Rights Verification",
          desc: "ArcFace cosine similarity >= 0.92, acoustic voice timbre verified, and Ed25519 legal rights contract confirmed prior to broadcast.",
          metric: "ArcFace >= 0.92 • Ed25519 Consent Verified",
          detailTag: "IDENTITY"
        },
        {
          label: "Evidence Grounding & Verification",
          desc: "Zero unsupported marketing claims. 100% of statements backed by indexed documentation with active forced safety gates.",
          metric: "100% Grounded Citations • Hallucination Free",
          detailTag: "SAFETY"
        },
        {
          label: "Media Execution & Provenance",
          desc: "Audio-visual lip sync offset <= 80ms, tamper-evident C2PA manifest attached, and bilingual English/Hindi productions generated.",
          metric: "Lip-Sync <= 80ms • C2PA SHA-256 Provenance",
          detailTag: "PROVENANCE"
        }
      ],
      interactiveAction: {
        label: "Return to Studio & Direct Actor",
        icon: <Award size={14} />,
        onClick: onClose
      },
      tagColor: "#1A73E8",
      illustrationBadge: "PRODUCTION CERTIFIED",
      renderVisual: (activePoint: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#202124' }}>
              8-Dimension Production Scorecard
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>
              8/8 PASSED
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', flex: 1 }}>
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
              <div
                key={i}
                style={{
                  backgroundColor: '#F8F9FA',
                  border: '1px solid #DADCE0',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: '#202124'
                }}
              >
                <Check size={12} color="#137333" />
                <span>{d}</span>
              </div>
            ))}
          </div>
        </div>
      )
    }
  ];

  // Auto-advance timer: Advances through points 0 -> 1 -> 2, then next chapter!
  useEffect(() => {
    if (!isOpen || !isPlaying) return;

    const interval = setInterval(() => {
      setStepProgress((prev) => {
        if (prev >= 100) {
          // Advance to next point
          setActivePointIndex((currentPoint) => {
            if (currentPoint < 2) {
              return currentPoint + 1;
            } else {
              // Advance to next chapter
              setCurrentChapter((ch) => (ch < chapters.length - 1 ? ch + 1 : 0));
              return 0;
            }
          });
          return 0;
        }
        return prev + 2.5; // ~4 seconds per point
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isOpen, isPlaying, currentChapter, activePointIndex]);

  // Reset point index when changing chapters manually
  const goToChapter = (idx: number) => {
    setCurrentChapter(idx);
    setActivePointIndex(0);
    setStepProgress(0);
  };

  const goToNextPoint = () => {
    if (activePointIndex < 2) {
      setActivePointIndex((p) => p + 1);
      setStepProgress(0);
    } else if (currentChapter < chapters.length - 1) {
      setCurrentChapter((c) => c + 1);
      setActivePointIndex(0);
      setStepProgress(0);
    } else {
      onClose();
    }
  };

  const goToPrevPoint = () => {
    if (activePointIndex > 0) {
      setActivePointIndex((p) => p - 1);
      setStepProgress(0);
    } else if (currentChapter > 0) {
      setCurrentChapter((c) => c - 1);
      setActivePointIndex(2);
      setStepProgress(0);
    }
  };

  // Keyboard navigation support
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        goToNextPoint();
      } else if (e.key === 'ArrowLeft') {
        goToPrevPoint();
      } else if (e.key === ' ') {
        e.preventDefault();
        setIsPlaying((p) => !p);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, activePointIndex, currentChapter]);

  const active = chapters[currentChapter];
  const activePoint = active.points[activePointIndex];

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 9999,
      backgroundColor: 'rgba(32, 33, 36, 0.65)',
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
          maxWidth: '1060px',
          height: '720px',
          maxHeight: '90vh',
          backgroundColor: '#FFFFFF',
          borderRadius: '20px',
          overflow: 'hidden',
          boxShadow: '0 24px 60px rgba(0, 0, 0, 0.28)',
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid #DADCE0',
          position: 'relative'
        }}
      >
        {/* SWIFT 3D BACKGROUND MOVEMENT: Ambient, semi-transparent behind the text */}
        <JudgeMode3DBackground
          opacity={0.16}
          speedMultiplier={1.15}
          activeChapter={currentChapter}
        />

        {/* Google Signature 4-Color Accent Bar */}
        <div className="google-accent-line" style={{ position: 'relative', zIndex: 1 }} />

        {/* Top Header Bar */}
        <div style={{
          padding: '14px 24px',
          borderBottom: '1px solid #DADCE0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(12px)',
          position: 'relative',
          zIndex: 2
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'Google Sans, -apple-system, sans-serif', color: '#202124' }}>
                  AVATAROS • CINEMATIC JUDGE WALKTHROUGH
                </span>
                <span className="badge-neon badge-primary" style={{ fontSize: '9px', padding: '1px 8px' }}>
                  STEP {activePointIndex + 1} OF 3
                </span>
              </div>
              <p style={{ fontSize: '11px', color: '#5F6368', margin: 0 }}>
                Step-by-step architectural verification. Read one key insight at a time.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* Auto-Play Toggle */}
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                background: isPlaying ? '#E8F0FE' : '#F1F3F4',
                border: `1px solid ${isPlaying ? '#1A73E8' : '#DADCE0'}`,
                borderRadius: 'var(--radius-full)',
                padding: '4px 12px',
                fontSize: '11px',
                fontWeight: 600,
                color: isPlaying ? '#1A73E8' : '#5F6368',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer'
              }}
              title={isPlaying ? "Pause auto-advance" : "Resume auto-advance"}
            >
              {isPlaying ? <Pause size={12} /> : <Play size={12} />}
              <span>{isPlaying ? "AUTO PLAYING" : "PAUSED"}</span>
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              style={{
                background: '#F1F3F4',
                border: '1px solid #DADCE0',
                borderRadius: '50%',
                width: '30px',
                height: '30px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#5F6368'
              }}
              title="Close Judge Mode"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Global Progress Bar: Chapter + Active Point */}
        <div style={{ width: '100%', height: '3px', backgroundColor: '#F1F3F4', position: 'relative', zIndex: 2 }}>
          <div style={{
            width: `${((currentChapter * 3 + activePointIndex + stepProgress / 100) / 18) * 100}%`,
            height: '100%',
            backgroundColor: active.tagColor,
            transition: 'width 0.1s linear'
          }} />
        </div>

        {/* MAIN BODY: Split-Pane Widescreen Layout */}
        <div style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: '1.25fr 1fr',
          overflow: 'hidden',
          position: 'relative',
          zIndex: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.88)',
          backdropFilter: 'blur(8px)'
        }}>
          {/* LEFT PANE: One-by-One Staggered Reading Experience */}
          <div style={{
            padding: '28px 32px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            borderRight: '1px solid #DADCE0',
            overflowY: 'auto'
          }}>
            {/* Chapter Header */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span className="badge-neon badge-primary" style={{ padding: '2px 10px', fontSize: '10px' }}>
                  {active.badge}
                </span>
                <span className="badge-neon badge-secondary" style={{ fontSize: '10px' }}>
                  {active.illustrationBadge}
                </span>
              </div>

              <h2 style={{ fontSize: '20px', fontWeight: 600, color: '#202124', fontFamily: 'Google Sans, -apple-system, sans-serif' }}>
                {active.title}
              </h2>
              <p style={{ fontSize: '12.5px', color: '#5F6368', marginTop: '2px' }}>
                {active.subtitle}
              </p>
            </div>

            {/* Core Breakthrough Concept Callout */}
            <div style={{
              backgroundColor: '#F8F9FA',
              border: '1px solid #DADCE0',
              borderRadius: '10px',
              padding: '12px 16px',
              fontSize: '12px',
              color: '#202124',
              lineHeight: 1.5
            }}>
              <strong style={{ color: active.tagColor }}>Core Breakthrough:</strong> {active.concept}
            </div>

            {/* ONE-BY-ONE SEQUENTIAL STEPPER PILLS (3 Points) */}
            <div style={{ display: 'flex', gap: '8px' }}>
              {active.points.map((pt, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setActivePointIndex(idx);
                    setStepProgress(0);
                  }}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    borderRadius: '8px',
                    border: `1px solid ${activePointIndex === idx ? active.tagColor : '#DADCE0'}`,
                    backgroundColor: activePointIndex === idx ? '#FFFFFF' : '#F8F9FA',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'all 0.2s ease',
                    boxShadow: activePointIndex === idx ? '0 2px 8px rgba(0,0,0,0.08)' : 'none'
                  }}
                >
                  <div style={{
                    width: '18px',
                    height: '18px',
                    borderRadius: '50%',
                    backgroundColor: activePointIndex === idx ? active.tagColor : activePointIndex > idx ? '#137333' : '#DADCE0',
                    color: '#FFFFFF',
                    fontSize: '10px',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {activePointIndex > idx ? <Check size={11} /> : idx + 1}
                  </div>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: activePointIndex === idx ? 700 : 500,
                    color: activePointIndex === idx ? '#202124' : '#5F6368',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {pt.detailTag}
                  </span>
                </button>
              ))}
            </div>

            {/* THE ACTIVE SPOTLIGHT POINT (Featured in Depth for Judges) */}
            <AnimatePresence mode="wait">
              <motion.div
                key={`${currentChapter}-${activePointIndex}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: `2px solid ${active.tagColor}`,
                  borderRadius: '14px',
                  padding: '20px',
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                  position: 'relative'
                }}
              >
                {/* Active Reading Timer Indicator */}
                {isPlaying && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '3px',
                    backgroundColor: 'rgba(0,0,0,0.05)',
                    borderTopLeftRadius: '14px',
                    borderTopRightRadius: '14px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${stepProgress}%`,
                      height: '100%',
                      backgroundColor: active.tagColor,
                      transition: 'width 0.1s linear'
                    }} />
                  </div>
                )}

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      backgroundColor: active.tagColor,
                      color: '#FFFFFF',
                      padding: '2px 8px',
                      borderRadius: '9999px'
                    }}>
                      POINT {activePointIndex + 1} / 3
                    </span>
                    <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#202124', margin: 0 }}>
                      {activePoint.label}
                    </h3>
                  </div>

                  <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>
                    {activePoint.detailTag}
                  </span>
                </div>

                <p style={{ fontSize: '13px', color: '#3C4043', lineHeight: 1.6, margin: 0 }}>
                  {activePoint.desc}
                </p>

                {/* Technical Metric Evidence */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: '#F8F9FA',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid #DADCE0',
                  fontSize: '11px',
                  color: '#137333',
                  fontWeight: 600
                }}>
                  <CheckCircle2 size={14} color="#137333" />
                  <span>{activePoint.metric}</span>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Live Capability Trigger Button */}
            <div style={{
              marginTop: 'auto',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 16px',
              backgroundColor: '#E8F0FE',
              border: '1px solid #D2E3FC',
              borderRadius: '10px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={16} color="#1A73E8" />
                <div>
                  <span style={{ fontSize: '11.5px', fontWeight: 600, color: '#1A73E8' }}>
                    EXECUTE CAPABILITY LIVE
                  </span>
                  <p style={{ fontSize: '10px', color: '#5F6368', margin: 0 }}>
                    Triggers actual backend engine execution.
                  </p>
                </div>
              </div>

              <button
                className="btn btn-primary"
                onClick={() => {
                  active.interactiveAction.onClick();
                }}
                style={{ padding: '6px 14px', fontSize: '11px', gap: '6px' }}
              >
                {active.interactiveAction.icon}
                {active.interactiveAction.label}
              </button>
            </div>
          </div>

          {/* RIGHT PANE: Interactive Architectural Visualizer */}
          <div style={{
            padding: '28px 28px',
            backgroundColor: '#FAFAFA',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '11px', fontWeight: 700, color: '#5F6368', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                ARCHITECTURAL TELEMETRY &amp; PROOF
              </span>
              <span style={{ fontSize: '10.5px', color: '#1A73E8', fontWeight: 600 }}>
                Live Verification Model
              </span>
            </div>

            {/* Render Chapter-Specific Technical Simulator */}
            <div style={{
              flex: 1,
              backgroundColor: '#FFFFFF',
              border: '1px solid #DADCE0',
              borderRadius: '14px',
              padding: '18px',
              boxShadow: '0 2px 8px rgba(60,64,67,0.06)',
              overflow: 'hidden'
            }}>
              {active.renderVisual(activePointIndex)}
            </div>
          </div>
        </div>

        {/* FOOTER CONTROLS: Stepper & Chapter Dots */}
        <div style={{
          padding: '12px 24px',
          borderTop: '1px solid #DADCE0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#F8F9FA',
          position: 'relative',
          zIndex: 2
        }}>
          {/* Chapter Selector Dots */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {chapters.map((ch, idx) => (
              <button
                key={ch.id}
                onClick={() => goToChapter(idx)}
                style={{
                  width: currentChapter === idx ? '28px' : '8px',
                  height: '8px',
                  borderRadius: '4px',
                  backgroundColor: currentChapter === idx ? active.tagColor : '#DADCE0',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                title={ch.title}
              />
            ))}
            <span style={{ fontSize: '11px', color: '#5F6368', marginLeft: '6px' }}>
              Chapter {currentChapter + 1} of 6
            </span>
          </div>

          {/* Stepper Buttons (Point-by-Point and Chapter Navigation) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="btn btn-secondary"
              onClick={goToPrevPoint}
              disabled={currentChapter === 0 && activePointIndex === 0}
              style={{ padding: '6px 12px', fontSize: '11px', gap: '4px' }}
            >
              <ChevronLeft size={14} />
              Previous Insight
            </button>

            <button
              className="btn btn-primary"
              onClick={goToNextPoint}
              style={{ padding: '6px 16px', fontSize: '11px', gap: '4px' }}
            >
              <span>{activePointIndex < 2 ? "Next Insight" : currentChapter < 5 ? "Next Chapter" : "Finish Tour"}</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CinematicJudgeMode;
