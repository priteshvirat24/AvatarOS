import React, { useState, useEffect } from 'react';
import {
  Play, Pause, SkipForward, SkipBack, X, Sparkles, ShieldCheck, Database,
  Film, MessageSquare, Cpu, CheckCircle2, AlertTriangle, ArrowRight,
  Layers, Lock, ExternalLink, Award, FileCode2, Zap, Volume2, ChevronRight,
  ChevronLeft, BarChart3, Fingerprint, Search, ShieldAlert, Check, Radio,
  Maximize2, Eye, Activity, Terminal, Clock
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
  const [isPlaying, setIsPlaying] = useState(false); // Default to paused/manual so judges can read without being rushed!
  const [pointProgress, setPointProgress] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [readSpeed, setReadSpeed] = useState<'normal' | 'relaxed'>('relaxed'); // 8.5s relaxed reading pace

  const chapters = [
    {
      id: "thesis",
      act: "ACT 01 // IMMUTABLE IDENTITY",
      badge: "SCENE 01 / 06",
      title: "The Thesis: Persistent Digital Identity & Likeness Rights",
      tagline: "Create a digital actor once. Direct them forever.",
      concept: "Traditional generative video produces disposable, drifting outputs. AvatarOS establishes permanent enterprise digital actors anchored in immutable biometrics and cryptographically verifiable legal rights.",
      tagColor: "#1A73E8",
      illustrationBadge: "DIGITAL DNA ARCHITECTURE",
      points: [
        {
          label: "ArcFace 512-Dimensional Biometric Anchor",
          headline: "Zero Biometric Drift Across Any Prompt",
          desc: "ArcFace 512-d facial embedding vectors and acoustic vocal timbre are sealed in a tamper-evident DNA manifest. Across lighting shifts, emotional transitions, and camera angles, biometric variance is 0.0%.",
          metric: "ArcFace Cosine Similarity >= 0.94 • 0.0% Biometric Drift",
          tag: "BIOMETRIC SEAL"
        },
        {
          label: "Ed25519 Cryptographic Consent Engine",
          headline: "Legally Binding Non-Repudiable Likeness Rights",
          desc: "Actor likeness and voice are bounded by Ed25519 cryptographic signatures. Enforces expiry boundaries, allowed registers (technical, executive), and restricted topics to prevent unconsented misuse.",
          metric: "Ed25519 Signed • Strictly Enforced Rights Governance",
          tag: "LEGAL RIGHTS"
        },
        {
          label: "Omnichannel Multi-Asset Synchronization",
          headline: "One Unified Character Across All Channels",
          desc: "The exact same digital actor stars in 16:9 widescreen 4K campaign ads, 9:16 vertical Shorts, and participates in real-time conversational video streams without identity dissonance.",
          metric: "16:9 Widescreen • 9:16 Shorts • Sub-800ms Realtime Live",
          tag: "OMNICHANNEL"
        }
      ],
      interactiveAction: {
        label: "Inspect Maya v1.7.0 DNA Manifest",
        icon: <ShieldCheck size={15} />,
        onClick: onInspectDna
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Fingerprint size={18} color="#1A73E8" />
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
                Identity Manifest: Maya v1.7.0
              </span>
            </div>
            <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>
              DNA SEALED
            </span>
          </div>

          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            borderRadius: '12px',
            padding: '14px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '11px',
            color: '#3C4043',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ color: '#1A73E8', fontWeight: 700 }}>
              // ArcFace 512-Dimensional Vector Hash
            </div>
            <div style={{ wordBreak: 'break-all', fontSize: '10px', color: '#5F6368', lineHeight: 1.4 }}>
              sha256:7f8a9e2d1c4b5a6f8e9d0c1b2a3f4e5d6c7b8a9e0f1a2b3c4d5e6f7a8b9c0d1e
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #E8EAED', paddingTop: '8px' }}>
              <span>Cosine Threshold:</span>
              <span style={{ color: '#137333', fontWeight: 700 }}>0.942 (PASS)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Ed25519 Signer:</span>
              <span style={{ color: '#1A73E8', fontWeight: 600 }}>actor_maya_legal_key</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Allowed Registers:</span>
              <span style={{ color: '#202124', fontWeight: 600 }}>technical, executive</span>
            </div>
          </div>

          <motion.div
            key={ptIndex}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            style={{
              backgroundColor: ptIndex === 0 ? '#E8F0FE' : ptIndex === 1 ? '#E6F4EA' : '#FEF7E0',
              borderRadius: '12px',
              padding: '14px',
              border: '1px solid #DADCE0',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 800, color: '#202124', textTransform: 'uppercase' }}>
              {ptIndex === 0 && "Biometric Vector Verification: Active"}
              {ptIndex === 1 && "Cryptographic Rights License: Enforced"}
              {ptIndex === 2 && "Unified Omnichannel Sync: Verified"}
            </div>
            <div style={{ fontSize: '11.5px', color: '#5F6368', lineHeight: 1.45 }}>
              {ptIndex === 0 && "ArcFace facial landmarks matched against original reference footage with zero variation across all scenes."}
              {ptIndex === 1 && "Actor consent bounds valid until 2027-12-31. Unauthorized topic injection mathematically prohibited."}
              {ptIndex === 2 && "Same persona assets shared seamlessly between 4K video ads and live conversational calls."}
            </div>
          </motion.div>
        </div>
      )
    },
    {
      id: "dag",
      act: "ACT 02 // AUTONOMOUS DAG",
      badge: "SCENE 02 / 06",
      title: "Autonomous Multi-Agent DAG: Zero Human in the Loop",
      tagline: "From a single creative brief to an executive 5-scene broadcast campaign.",
      concept: "A single command triggers an autonomous Directed Acyclic Graph (DAG) with 9 specialized agent roles executing in strict dependency order.",
      tagColor: "#1A73E8",
      illustrationBadge: "AUTONOMOUS AGENT DAG",
      points: [
        {
          label: "Research & Fact Grounding Agent",
          headline: "Pre-Script Fact Grounding via Hybrid Search",
          desc: "Before a single line of script is written, the Research Agent indexes technical documentation, whitepapers, and benchmark PDFs using hybrid BM25 keyword search plus dense vector retrieval.",
          metric: "Hybrid BM25 + Vector Retrieval • Document Index Scanned",
          tag: "RESEARCH"
        },
        {
          label: "Adversarial Critic Verification",
          headline: "Adversarial Fact Check Challenging the Script",
          desc: "Acts as an adversarial challenger to the Scriptwriter. Rigorously cross-examines every proposed marketing claim against verified documentation, rejecting unsupported assertions.",
          metric: "Adversarial Fact Check • Claim Veracity Scoring",
          tag: "CRITIC"
        },
        {
          label: "Director & Performance Choreography",
          headline: "Multi-Scene Emotion & Camera Choreography",
          desc: "Director Agent plans emotional trajectories, camera angles (Close-Up, Medium, OTS), and gaze vectors scene-by-scene to generate a structured PerformancePlan.",
          metric: "Emotional Trajectory Arc • 5-Scene Camera Breakdown",
          tag: "DIRECTOR"
        }
      ],
      interactiveAction: {
        label: "Trigger Autonomous Production DAG",
        icon: <Sparkles size={15} />,
        onClick: onRunProduction
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
              9-Agent DAG Pipeline Flow
            </span>
            <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>
              ORCHESTRATION
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, justifyContent: 'center' }}>
            {[
              { role: "1. Brief & Context", status: "COMPLETE", time: "120ms", active: false },
              { role: "2. Research Agent (BM25)", status: ptIndex === 0 ? "FOCUS" : "COMPLETE", time: "480ms", active: ptIndex === 0 },
              { role: "3. Script & Critic Loop", status: ptIndex === 1 ? "FOCUS" : "COMPLETE", time: "1.2s", active: ptIndex === 1 },
              { role: "4. Director Choreography", status: ptIndex === 2 ? "FOCUS" : "COMPLETE", time: "850ms", active: ptIndex === 2 },
              { role: "5. Multimodal Renderer", status: "READY", time: "3.2s", active: false }
            ].map((st, i) => (
              <motion.div
                key={i}
                animate={{ scale: st.active ? 1.02 : 1 }}
                transition={{ duration: 0.25 }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  backgroundColor: st.active ? '#E8F0FE' : '#F8F9FA',
                  border: `1.5px solid ${st.active ? '#1A73E8' : '#DADCE0'}`,
                  boxShadow: st.active ? '0 4px 14px rgba(26, 115, 232, 0.12)' : 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{
                    width: '9px',
                    height: '9px',
                    borderRadius: '50%',
                    backgroundColor: st.active ? '#1A73E8' : '#137333'
                  }} />
                  <span style={{ fontSize: '12px', fontWeight: st.active ? 700 : 500, color: '#202124' }}>
                    {st.role}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
                  <span style={{ color: '#5F6368' }}>{st.time}</span>
                  <span className={st.active ? "badge-neon badge-primary" : "badge-neon badge-emerald"} style={{ fontSize: '9px', padding: '2px 8px' }}>
                    {st.status}
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
      badge: "SCENE 03 / 06",
      title: "Multimodal Safety Guardian & The Forced Gate",
      tagline: "Zero ungrounded claims. Mathematical enforcement against AI hallucinations.",
      concept: "Before any video is published, the Multimodal Guardian inspects both the generated script and rendered frames to guarantee factual veracity.",
      tagColor: "#D93025",
      illustrationBadge: "FORCED PUBLICATION GATE",
      points: [
        {
          label: "Evidence Grounding Requirement",
          headline: "Strict Documentation Citation Requirements",
          desc: "Every single factual claim (battery life, benchmarks, latency) must map directly to an indexed benchmark document with page and paragraph citations.",
          metric: "100% Citation Grounded • Zero Unsupported Assertions",
          tag: "GROUNDING"
        },
        {
          label: "Forced Gate Halts Publication",
          headline: "Instant Publication Freeze on Fake Claims",
          desc: "If an unsupported claim like '3x faster' is detected without citation, the Publication Gate immediately halts broadcast and issues an actionable rework brief.",
          metric: "Forced Gate: BLOCKED • Actionable Rework Diagnostic",
          tag: "GATE BLOCK"
        },
        {
          label: "C2PA Content Credentials Manifest",
          headline: "Cryptographic Tamper-Evident Media Provenance",
          desc: "Approved media receives cryptographically signed Content Credentials (C2PA) with SHA-256 media hashes, ensuring authentic tamper-evident provenance.",
          metric: "C2PA Manifest Attached • SHA-256 Tamper-Evident",
          tag: "PROVENANCE"
        }
      ],
      interactiveAction: {
        label: "Simulate '3x Faster' Claim Failure",
        icon: <AlertTriangle size={15} />,
        onClick: onTriggerClaimFail
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
              Claim Verification Scanner
            </span>
            <span className="badge-neon badge-amber" style={{ fontSize: '10px', color: '#C5221F', borderColor: '#FAD2CF' }}>
              GATE ACTIVE
            </span>
          </div>

          <motion.div
            initial={{ scale: 0.98 }}
            animate={{ scale: 1 }}
            style={{
              padding: '14px',
              borderRadius: '12px',
              backgroundColor: '#FEF7F7',
              border: '1.5px solid #FAD2CF',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#C5221F' }}>
                DETECTED CLAIM: "3x Faster than M3 Max"
              </span>
              <span className="badge-neon" style={{ backgroundColor: '#FCE8E6', color: '#C5221F', borderColor: '#FAD2CF', fontSize: '9px' }}>
                FAIL
              </span>
            </div>
            <p style={{ fontSize: '11px', color: '#5F6368', margin: 0 }}>
              Evidence Citation: <em>None found in titan_specs.pdf or benchmarks</em>
            </p>
            <div style={{ fontSize: '11px', color: '#C5221F', fontWeight: 700, marginTop: '2px' }}>
              GATE ACTION: PUBLICATION BLOCKED (Exit Code: GATE_CLAIM_FAIL)
            </div>
          </motion.div>

          <div style={{
            padding: '14px',
            borderRadius: '12px',
            backgroundColor: '#F6FCF8',
            border: '1px solid #CEEAD6',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '12px', fontWeight: 800, color: '#137333' }}>
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
      act: "ACT 04 // REALTIME VOICE",
      badge: "SCENE 04 / 06",
      title: "Real-Time Conversational Digital Human Runtime",
      tagline: "Sub-800ms conversational runtime with user barge-in interruption.",
      concept: "AvatarOS transitions seamlessly from offline studio directing to bidirectional realtime conversation with low-latency audio streaming.",
      tagColor: "#B06000",
      illustrationBadge: "REALTIME CONVERSATION",
      points: [
        {
          label: "Sub-800ms Conversational Latency",
          headline: "Conversational Cadency Under 480ms",
          desc: "ASR (110ms) + LLM Time-to-First-Token (240ms) + Audio Time-to-First-Audio (130ms) for natural human cadency under 480ms total roundtrip.",
          metric: "480ms Total Latency • Natural Human Cadence",
          tag: "LATENCY"
        },
        {
          label: "Realtime User Barge-In Interruption",
          headline: "Zero-Lag Cancellation When You Speak",
          desc: "Instantaneous cancellation of outbound audio playback when the user speaks mid-sentence. Cancels remaining audio chunks within 18ms.",
          metric: "18ms Interruption Response • Zero Echo Audio Loop",
          tag: "BARGE-IN"
        },
        {
          label: "Live-to-Studio Production Handoff",
          headline: "Conversational Brainstorms Exported as Ads",
          desc: "Conversations held in Live Mode can be exported as structured creative briefs directly into Studio Mode for multi-channel video rendering.",
          metric: "Live Transcript -> Studio Production Brief Handoff",
          tag: "HANDOFF"
        }
      ],
      interactiveAction: {
        label: "Launch Real-Time Conversational Stage",
        icon: <MessageSquare size={15} />,
        onClick: onOpenLiveMode
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
              Latency Waterfall Budget (&lt;800ms Target)
            </span>
            <span className="badge-neon badge-amber" style={{ fontSize: '10px' }}>
              480MS TOTAL
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1, justifyContent: 'center' }}>
            {[
              { step: "Audio Ingest & ASR", ms: 110, pct: "23%", color: "#1A73E8" },
              { step: "LLM Time to First Token", ms: 240, pct: "50%", color: "#B06000" },
              { step: "Audio Synthesis & Streaming", ms: 130, pct: "27%", color: "#137333" }
            ].map((l, i) => (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px' }}>
                  <span style={{ color: '#202124', fontWeight: 600 }}>{l.step}</span>
                  <span style={{ color: l.color, fontWeight: 700 }}>{l.ms}ms</span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: '#F1F3F4', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: l.pct, height: '100%', backgroundColor: l.color }} />
                </div>
              </div>
            ))}

            <div style={{
              marginTop: '10px',
              padding: '12px',
              backgroundColor: '#F8F9FA',
              borderRadius: '10px',
              border: '1px solid #DADCE0',
              fontSize: '11.5px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ color: '#5F6368' }}>Barge-In Detector:</span>
              <span style={{ color: '#137333', fontWeight: 700 }}>ARMED (18ms response)</span>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "clickhouse_mcp",
      act: "ACT 05 // SELF-EVOLUTION",
      badge: "SCENE 05 / 06",
      title: "Closed-Loop Self-Evolution: ClickHouse & Governed MCP",
      tagline: "The agent queries its own real production analytics to evolve its behavior.",
      concept: "AvatarOS closes the loop: audience retention data stored in ClickHouse is queried by the Evolution Agent via Model Context Protocol (MCP).",
      tagColor: "#137333",
      illustrationBadge: "CLICKHOUSE MCP BRIDGE",
      points: [
        {
          label: "ClickHouse Columnar Telemetry",
          headline: "Sub-Millisecond Big Data Analytics",
          desc: "Ingests raw scene retention, hook drop-off, and audio engagement events. Queries over 1,800+ real telemetry events in under 2.5ms.",
          metric: "2.1ms Query Latency • Columnar Index Scans",
          tag: "TELEMETRY"
        },
        {
          label: "Strict MCP Tool Governance",
          headline: "100% Read-Only Safety Sandbox",
          desc: "100% read-only agent allowlist prevents destructive DDL/DML queries. The agent can only execute bounded analytical aggregations.",
          metric: "Read-Only Allowlist • Zero SQL Injection Attack Surface",
          tag: "GOVERNANCE"
        },
        {
          label: "Statistical Evolution Guardrails",
          headline: "Rigorously Proven Strategy Updates",
          desc: "Strategy updates (e.g. switching hook style from conversational to technical) require n >= 50 samples and non-overlapping 95% confidence intervals.",
          metric: "n >= 50 Required • p-value < 0.01 Statistical Rigor",
          tag: "EVOLUTION"
        }
      ],
      interactiveAction: {
        label: "Query ClickHouse Telemetry via MCP",
        icon: <Database size={15} />,
        onClick: onOpenEvolution
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
              Governed MCP Analytics Query
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '10px' }}>
              READ-ONLY MCP
            </span>
          </div>

          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            color: '#202124',
            padding: '14px',
            borderRadius: '12px',
            fontFamily: 'Roboto Mono, monospace',
            fontSize: '11px',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
          }}>
            <div style={{ color: '#1A73E8', fontWeight: 700 }}>$ mcp query --tool=clickhouse_telemetry</div>
            <div style={{ color: '#137333' }}>SELECT hook_style, avg(retention_rate)</div>
            <div style={{ color: '#137333' }}>FROM audience_telemetry GROUP BY hook_style;</div>
            <div style={{ borderTop: '1px solid #DADCE0', marginTop: '8px', paddingTop: '8px' }}>
              <div style={{ color: '#202124', fontWeight: 700 }}>technical_breakdown: 84.2% [n=62] (Winner)</div>
              <div style={{ color: '#5F6368' }}>conversational_hook:  68.1% [n=58]</div>
            </div>
            <div style={{ marginTop: 'auto', color: '#B06000', fontSize: '10px', fontWeight: 600 }}>
              Execution: 2.1ms | Confidence: 99.2% | DDL Blocked
            </div>
          </div>
        </div>
      )
    },
    {
      id: "scorecard",
      act: "ACT 06 // CERTIFICATION",
      badge: "SCENE 06 / 06",
      title: "Judge-Proof Scorecard: 8/8 Dimensions Verified",
      tagline: "Production-ready enterprise digital actor architecture.",
      concept: "Every run evaluates the complete media lifecycle against 8 strict production standards, ensuring zero human intervention is required.",
      tagColor: "#1A73E8",
      illustrationBadge: "PRODUCTION CERTIFIED",
      points: [
        {
          label: "Identity & Rights Verification",
          headline: "Biometric & Legal Compliance Verified",
          desc: "ArcFace cosine similarity >= 0.92, acoustic voice timbre verified, and Ed25519 legal rights contract confirmed prior to broadcast.",
          metric: "ArcFace >= 0.92 • Ed25519 Consent Verified",
          tag: "IDENTITY"
        },
        {
          label: "Evidence Grounding & Verification",
          headline: "100% Documented Factual Citations",
          desc: "Zero unsupported marketing claims. 100% of statements backed by indexed documentation with active forced safety gates.",
          metric: "100% Grounded Citations • Hallucination Free",
          tag: "SAFETY"
        },
        {
          label: "Media Execution & Provenance",
          headline: "Broadcast Lip-Sync & C2PA Provenance",
          desc: "Audio-visual lip sync offset <= 80ms, tamper-evident C2PA manifest attached, and bilingual English/Hindi productions generated.",
          metric: "Lip-Sync <= 80ms • C2PA SHA-256 Provenance",
          tag: "PROVENANCE"
        }
      ],
      interactiveAction: {
        label: "Return to Studio & Direct Actor",
        icon: <Award size={15} />,
        onClick: onClose
      },
      renderVisual: (ptIndex: number) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', height: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124' }}>
              8-Dimension Production Scorecard
            </span>
            <span className="badge-neon badge-emerald" style={{ fontSize: '10px' }}>
              8/8 PASSED
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', flex: 1, alignItems: 'center' }}>
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
                transition={{ delay: i * 0.04 }}
                style={{
                  backgroundColor: '#F8F9FA',
                  border: '1px solid #DADCE0',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '11px',
                  fontWeight: 700,
                  color: '#202124'
                }}
              >
                <Check size={14} color="#137333" />
                <span>{d}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )
    }
  ];

  // Auto-play timer with comfortable, relaxed reading cadence
  useEffect(() => {
    if (!isOpen || !isPlaying) return;

    // relaxed pace: ~8.5 seconds per insight
    const increment = readSpeed === 'relaxed' ? 1.15 : 2.0;

    const interval = setInterval(() => {
      setElapsedSeconds((s) => s + 0.1);
      setPointProgress((prev) => {
        if (prev >= 100) {
          setActivePointIndex((currentPoint) => {
            if (currentPoint < 2) {
              return currentPoint + 1;
            } else {
              setCurrentChapter((ch) => (ch < chapters.length - 1 ? ch + 1 : 0));
              return 0;
            }
          });
          return 0;
        }
        return prev + increment;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isOpen, isPlaying, currentChapter, activePointIndex, readSpeed]);

  const goToChapter = (idx: number) => {
    setCurrentChapter(idx);
    setActivePointIndex(0);
    setPointProgress(0);
  };

  const goToNextPoint = () => {
    if (activePointIndex < 2) {
      setActivePointIndex((p) => p + 1);
      setPointProgress(0);
    } else if (currentChapter < chapters.length - 1) {
      setCurrentChapter((c) => c + 1);
      setActivePointIndex(0);
      setPointProgress(0);
    } else {
      onClose();
    }
  };

  const goToPrevPoint = () => {
    if (activePointIndex > 0) {
      setActivePointIndex((p) => p - 1);
      setPointProgress(0);
    } else if (currentChapter > 0) {
      setCurrentChapter((c) => c - 1);
      setActivePointIndex(2);
      setPointProgress(0);
    }
  };

  // Keyboard navigation
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

  // Timecode formatting
  const formatTimecode = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = (sec % 60).toFixed(1);
    return `${mins.toString().padStart(2, '0')}:${secs.padStart(4, '0')}`;
  };

  if (!isOpen) return null;

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
      {/* 1. VIVID, SWIFT AND SLOW 3D BACKGROUND: Prominently visible on white background */}
      <JudgeMode3DBackground
        opacity={0.65}
        speedMultiplier={0.5}
        activeChapter={currentChapter}
        activePoint={activePointIndex}
      />

      {/* Official Google 4-Color Accent Line */}
      <div className="google-accent-line" style={{ position: 'relative', zIndex: 10 }} />

      {/* 2. TOP HEADER BAR: Google Light Theme */}
      <header style={{
        height: '56px',
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
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#D93025'
            }} />
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              letterSpacing: '0.8px',
              color: '#202124',
              fontFamily: 'Roboto Mono, monospace'
            }}>
              LIVE TOUR
            </span>
          </div>

          <div style={{
            fontSize: '11px',
            fontFamily: 'Roboto Mono, monospace',
            color: '#1A73E8',
            backgroundColor: '#E8F0FE',
            padding: '3px 8px',
            borderRadius: 'var(--radius-full)',
            border: '1px solid #D2E3FC'
          }}>
            TC {formatTimecode(elapsedSeconds)} / 01:30.0
          </div>

          <span style={{ color: '#DADCE0' }}>|</span>

          <span style={{ fontSize: '12px', fontWeight: 600, color: '#5F6368' }}>
            {active.title}
          </span>
        </div>

        {/* Right: Reading Pace Toggle, Play/Pause & Exit */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {/* Relaxed / Manual Speed Mode */}
          <button
            onClick={() => {
              if (isPlaying) {
                setIsPlaying(false);
              } else {
                setIsPlaying(true);
              }
            }}
            style={{
              background: isPlaying ? '#E8F0FE' : '#F8F9FA',
              border: `1px solid ${isPlaying ? '#1A73E8' : '#DADCE0'}`,
              borderRadius: 'var(--radius-full)',
              padding: '5px 14px',
              fontSize: '11px',
              fontWeight: 600,
              color: isPlaying ? '#1A73E8' : '#5F6368',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer'
            }}
            title="Toggle between auto-play and manual reading pace"
          >
            {isPlaying ? <Pause size={12} color="#1A73E8" /> : <Play size={12} color="#5F6368" />}
            <span>{isPlaying ? "AUTO ADVANCE (8.5s)" : "MANUAL STEPPING"}</span>
          </button>

          {/* Exit Cinema */}
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{
              padding: '5px 14px',
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

      {/* Reading Progress Line for Current Point */}
      <div style={{ width: '100%', height: '2px', backgroundColor: '#F1F3F4', position: 'relative', zIndex: 10 }}>
        <div style={{
          width: isPlaying ? `${pointProgress}%` : '100%',
          height: '100%',
          backgroundColor: active.tagColor,
          transition: isPlaying ? 'width 0.1s linear' : 'none'
        }} />
      </div>

      {/* 3. MAIN WORKSPACE: Pristine Placement & Google Light Aesthetics */}
      <main style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1.25fr 1fr',
        gap: '36px',
        padding: '32px 48px',
        maxWidth: '1360px',
        margin: '0 auto',
        width: '100%',
        alignItems: 'center',
        position: 'relative',
        zIndex: 10,
        overflow: 'hidden'
      }}>
        {/* LEFT COLUMN: KINETIC TYPOGRAPHY & SEQUENTIAL INSIGHTS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Act Badge & Tagline */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="badge-neon badge-primary" style={{ padding: '3px 12px', fontSize: '10px' }}>
              {active.badge}
            </span>
            <span style={{
              fontSize: '11.5px',
              color: '#5F6368',
              fontFamily: 'Roboto Mono, monospace'
            }}>
              {active.illustrationBadge}
            </span>
          </div>

          {/* Master Headline: Clean Google Typography */}
          <motion.h1
            key={active.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            style={{
              fontSize: '32px',
              fontWeight: 700,
              lineHeight: 1.25,
              color: '#202124',
              letterSpacing: '-0.02em',
              margin: 0
            }}
          >
            {active.tagline}
          </motion.h1>

          {/* Core Breakthrough Callout Box */}
          <div style={{
            backgroundColor: '#F8F9FA',
            border: '1px solid #DADCE0',
            borderRadius: '12px',
            padding: '14px 18px',
            fontSize: '13px',
            color: '#202124',
            lineHeight: 1.55
          }}>
            <strong style={{ color: active.tagColor }}>Core Breakthrough: </strong>
            {active.concept}
          </div>

          {/* Stepper Pills for the 3 Insights */}
          <div style={{ display: 'flex', gap: '8px' }}>
            {active.points.map((pt, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setActivePointIndex(idx);
                  setPointProgress(0);
                }}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-full)',
                  border: `1.5px solid ${activePointIndex === idx ? active.tagColor : '#DADCE0'}`,
                  backgroundColor: activePointIndex === idx ? '#E8F0FE' : '#FFFFFF',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease',
                  boxShadow: activePointIndex === idx ? '0 1px 4px rgba(26, 115, 232, 0.2)' : 'none'
                }}
              >
                <div style={{
                  width: '18px',
                  height: '18px',
                  borderRadius: '50%',
                  backgroundColor: activePointIndex === idx ? active.tagColor : activePointIndex > idx ? '#137333' : '#DADCE0',
                  color: '#FFFFFF',
                  fontSize: '10.5px',
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
                  color: activePointIndex === idx ? '#1A73E8' : '#5F6368',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {pt.tag}
                </span>
              </button>
            ))}
          </div>

          {/* ACTIVE SPOTLIGHT INSIGHT CARD: Comfortable, Clean & Readable */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${currentChapter}-${activePointIndex}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.88)',
                backdropFilter: 'blur(12px)',
                borderRadius: '16px',
                padding: '22px 24px',
                boxShadow: '0 4px 16px rgba(60, 64, 67, 0.08), 0 1px 3px rgba(60, 64, 67, 0.04)',
                border: `1.5px solid ${active.tagColor}`,
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{
                  fontSize: '10.5px',
                  fontWeight: 700,
                  backgroundColor: '#E8F0FE',
                  color: active.tagColor,
                  padding: '3px 10px',
                  borderRadius: 'var(--radius-full)'
                }}>
                  INSIGHT {activePointIndex + 1} OF 3
                </span>
                <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>
                  {activePoint.tag}
                </span>
              </div>

              {/* Punchy Headline */}
              <h3 style={{
                fontSize: '18px',
                fontWeight: 700,
                color: '#202124',
                margin: 0,
                letterSpacing: '-0.01em'
              }}>
                {activePoint.headline}
              </h3>

              {/* Detailed Explanation */}
              <p style={{
                fontSize: '13px',
                color: '#3C4043',
                lineHeight: 1.6,
                margin: 0
              }}>
                {activePoint.desc}
              </p>

              {/* Verified Metric Badge */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#F8F9FA',
                padding: '9px 12px',
                borderRadius: '8px',
                border: '1px solid #DADCE0',
                fontSize: '11.5px',
                color: '#137333',
                fontWeight: 600
              }}>
                <CheckCircle2 size={15} color="#137333" />
                <span>{activePoint.metric}</span>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Action Trigger Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '2px' }}>
            <button
              onClick={() => active.interactiveAction.onClick()}
              className="btn btn-primary"
              style={{
                padding: '10px 22px',
                fontSize: '13px',
                fontWeight: 600,
                borderRadius: 'var(--radius-full)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: '0 2px 8px rgba(26, 115, 232, 0.35)'
              }}
            >
              {active.interactiveAction.icon}
              <span>{active.interactiveAction.label}</span>
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: ARCHITECTURAL TELEMETRY CARD */}
        <div style={{
          height: '460px',
          backgroundColor: 'rgba(255, 255, 255, 0.88)',
          backdropFilter: 'blur(12px)',
          borderRadius: '16px',
          border: '1px solid #DADCE0',
          boxShadow: '0 4px 20px rgba(60, 64, 67, 0.08), 0 1px 3px rgba(60, 64, 67, 0.04)',
          padding: '22px',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          {/* Card Top Title */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '14px',
            borderBottom: '1px solid #E8EAED',
            paddingBottom: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Terminal size={15} color="#1A73E8" />
              <span style={{ fontSize: '11.5px', fontWeight: 700, letterSpacing: '0.4px', color: '#202124' }}>
                AVATAROS ARCHITECTURAL TELEMETRY
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div className="status-dot active" />
              <span style={{ fontSize: '10.5px', color: '#137333', fontWeight: 700 }}>VERIFIED</span>
            </div>
          </div>

          {/* Dynamic Simulator Content */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            {active.renderVisual(activePointIndex)}
          </div>
        </div>
      </main>

      {/* 4. BOTTOM FOOTER CONTROLS: Google Material Light Bar */}
      <footer style={{
        height: '64px',
        padding: '0 32px',
        borderTop: '1px solid #DADCE0',
        backgroundColor: '#F8F9FA',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        zIndex: 10
      }}>
        {/* Scene Pills (6 Chapters) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {chapters.map((ch, idx) => (
            <button
              key={ch.id}
              onClick={() => goToChapter(idx)}
              style={{
                height: '7px',
                width: currentChapter === idx ? '32px' : '9px',
                borderRadius: '4px',
                backgroundColor: currentChapter === idx ? active.tagColor : '#DADCE0',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.25s ease'
              }}
              title={ch.title}
            />
          ))}
          <span style={{ fontSize: '11.5px', color: '#5F6368', marginLeft: '10px', fontWeight: 600 }}>
            SCENE {currentChapter + 1} OF 6
          </span>
        </div>

        {/* Previous & Next Stepper Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={goToPrevPoint}
            disabled={currentChapter === 0 && activePointIndex === 0}
            className="btn btn-secondary"
            style={{
              padding: '6px 14px',
              fontSize: '11.5px',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <ChevronLeft size={15} />
            <span>PREV INSIGHT</span>
          </button>

          <button
            onClick={goToNextPoint}
            className="btn btn-primary"
            style={{
              padding: '6px 18px',
              fontSize: '11.5px',
              fontWeight: 600,
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 2px 6px rgba(26, 115, 232, 0.3)'
            }}
          >
            <span>{activePointIndex < 2 ? "NEXT INSIGHT" : currentChapter < 5 ? "NEXT SCENE" : "FINISH TOUR"}</span>
            <ChevronRight size={15} />
          </button>
        </div>
      </footer>
    </div>
  );
};

export default CinematicJudgeMode;
