import React from 'react';
import {
  Film, Sparkles, MessageSquare, Database, ShieldCheck, ArrowRight,
  CheckCircle2, AlertTriangle, Layers, Dna, Cpu, Zap, Activity,
  Award, Globe, Play, Lock, ExternalLink, FileSearch, ShieldAlert, BarChart3,
  Search, Shield, Check, RefreshCw
} from 'lucide-react';
import { motion } from 'framer-motion';
import { GoogleLabs3D } from './GoogleLabs3D';

interface HomePageProps {
  onNavigate: (page: 'home' | 'studio' | 'live' | 'evolution' | 'knowledge' | 'cast') => void;
  onOpenJudgeMode: () => void;
  onInspectDna: () => void;
  onLaunchPreset?: (brief: string) => void;
  onTriggerClaimDemo?: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  onNavigate,
  onOpenJudgeMode,
  onInspectDna,
  onLaunchPreset,
  onTriggerClaimDemo
}) => {
  return (
    <div style={{
      flex: 1,
      overflowY: 'auto',
      backgroundColor: 'var(--color-background)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* 1. HERO SECTION: The Killer Hook */}
      <section style={{
        padding: '56px 32px 40px 32px',
        maxWidth: '1280px',
        margin: '0 auto',
        width: '100%',
        display: 'grid',
        gridTemplateColumns: '1.15fr 1fr',
        gap: '44px',
        alignItems: 'center'
      }}>
        {/* Left Hero Copy */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}
        >
          {/* Top Pill Chip */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', alignSelf: 'flex-start', flexWrap: 'wrap' }}>
            <span className="badge-neon badge-primary" style={{ padding: '4px 14px', fontSize: '11px', fontWeight: 600 }}>
              ENTERPRISE AGENTIC PLATFORM • DIGITAL HUMAN RUNTIME
            </span>
            <span className="badge-neon badge-emerald" style={{ padding: '4px 12px', fontSize: '11px' }}>
              AUTONOMOUS PRODUCTION
            </span>
            <span className="badge-neon badge-amber" style={{ padding: '4px 12px', fontSize: '11px' }}>
              CLICKHOUSE MCP
            </span>
          </div>

          {/* Master Headline: The Hook */}
          <h1 style={{
            fontSize: '48px',
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: '-0.02em',
            color: '#202124',
            fontFamily: 'Google Sans, -apple-system, sans-serif'
          }}>
            Create a digital actor once.{' '}
            <span style={{
              background: 'linear-gradient(135deg, #1A73E8 0%, #174EA6 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Direct them forever.
            </span>
          </h1>

          {/* Subtitle */}
          <p style={{
            fontSize: '16.5px',
            color: '#5F6368',
            lineHeight: 1.6,
            maxWidth: '560px'
          }}>
            AvatarOS is the agentic infrastructure for persistent digital humans. Grounded in immutable Digital DNA, governed by cryptographic likeness rights, and guarded against hallucinations by multimodal verification gates.
          </p>

          {/* Action Button Cluster */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', marginTop: '6px' }}>
            <button
              className="btn btn-primary"
              onClick={() => onNavigate('studio')}
              style={{ padding: '12px 26px', fontSize: '14px', gap: '8px', fontWeight: 600 }}
            >
              <Film size={16} />
              Launch Studio Mode
              <ArrowRight size={15} />
            </button>

            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('live')}
              style={{ padding: '12px 22px', fontSize: '14px', gap: '8px', fontWeight: 500 }}
            >
              <Zap size={16} color="#1A73E8" />
              Talk to Maya Live (&lt;800ms)
            </button>

            <button
              className="btn judge-mode-btn"
              onClick={onOpenJudgeMode}
              style={{ padding: '12px 20px', fontSize: '14px', gap: '8px' }}
            >
              <Award size={16} color="#FFD700" />
              Cinematic Judge Tour
            </button>
          </div>

          {/* Quick Metrics Bar */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '16px',
            paddingTop: '20px',
            borderTop: '1px solid #DADCE0',
            marginTop: '8px'
          }}>
            <div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'Google Sans, sans-serif', color: '#1A73E8' }}>
                &lt; 800ms
              </div>
              <span style={{ fontSize: '11px', color: '#5F6368', fontWeight: 500 }}>Realtime Live Latency</span>
            </div>
            <div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'Google Sans, sans-serif', color: '#137333' }}>
                0.0% Drift
              </div>
              <span style={{ fontSize: '11px', color: '#5F6368', fontWeight: 500 }}>ArcFace 512-d Biometrics</span>
            </div>
            <div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'Google Sans, sans-serif', color: '#B06000' }}>
                100% Grounded
              </div>
              <span style={{ fontSize: '11px', color: '#5F6368', fontWeight: 500 }}>Evidence Safety Gate</span>
            </div>
          </div>
        </motion.div>

        {/* Right Hero: Live 3D Interactive Showcase */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          style={{
            position: 'relative',
            height: '460px',
            width: '100%',
            borderRadius: '20px',
            overflow: 'hidden',
            boxShadow: '0 8px 30px rgba(60,64,67,0.12), 0 1px 3px rgba(60,64,67,0.1)',
            border: '1px solid #DADCE0',
            backgroundColor: '#FFFFFF'
          }}
        >
          <GoogleLabs3D
            characterName="Maya"
            characterVersion="v1.7.0"
            isSpeaking={false}
            isListening={false}
            energy={0.82}
            height="100%"
          />
        </motion.div>
      </section>

      {/* 2. INTERACTIVE DEMO PRESET LAUNCHER: Instant One-Click Action */}
      <section style={{
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid #DADCE0',
        borderBottom: '1px solid #DADCE0',
        padding: '28px 32px'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={16} color="#1A73E8" />
              <span style={{ fontSize: '13px', fontWeight: 700, color: '#202124', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Quick Experience Presets
              </span>
              <span style={{ fontSize: '12px', color: '#5F6368' }}>
                — Click any preset to test the live autonomous runtime:
              </span>
            </div>
            <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>
              1-CLICK RUNTIME DEMO
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
            {/* Preset 1: Titan Keynote */}
            <div
              onClick={() => {
                if (onLaunchPreset) {
                  onLaunchPreset("Create a 60-second product launch for Indian developers. Research our documentation first. Do not make unsupported claims. Produce English and Hindi versions.");
                } else {
                  onNavigate('studio');
                }
              }}
              style={{
                backgroundColor: '#F8F9FA',
                border: '1px solid #DADCE0',
                borderRadius: '12px',
                padding: '16px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#1A73E8';
                e.currentTarget.style.backgroundColor = '#F8FBFF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#DADCE0';
                e.currentTarget.style.backgroundColor = '#F8F9FA';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px' }}>🎬</span>
                <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>STUDIO</span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#202124' }}>Titan Dev Keynote</div>
              <div style={{ fontSize: '11px', color: '#5F6368', lineHeight: 1.4 }}>
                60s launch video in English &amp; Hindi with research citations.
              </div>
            </div>

            {/* Preset 2: Trigger Safety Gate */}
            <div
              onClick={() => {
                if (onTriggerClaimDemo) {
                  onTriggerClaimDemo();
                } else {
                  onNavigate('studio');
                }
              }}
              style={{
                backgroundColor: '#F8F9FA',
                border: '1px solid #DADCE0',
                borderRadius: '12px',
                padding: '16px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#D93025';
                e.currentTarget.style.backgroundColor = '#FEF7F7';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#DADCE0';
                e.currentTarget.style.backgroundColor = '#F8F9FA';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px' }}>🛡️</span>
                <span className="badge-neon badge-amber" style={{ fontSize: '9px', color: '#C5221F', borderColor: '#FAD2CF', backgroundColor: '#FCE8E6' }}>SAFETY GATE</span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#202124' }}>Simulate Claim Block</div>
              <div style={{ fontSize: '11px', color: '#5F6368', lineHeight: 1.4 }}>
                Inject fake "3x faster" claim. Watch Guardian halt publication.
              </div>
            </div>

            {/* Preset 3: Gemini Live Audio */}
            <div
              onClick={() => onNavigate('live')}
              style={{
                backgroundColor: '#F8F9FA',
                border: '1px solid #DADCE0',
                borderRadius: '12px',
                padding: '16px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#1A73E8';
                e.currentTarget.style.backgroundColor = '#F8FBFF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#DADCE0';
                e.currentTarget.style.backgroundColor = '#F8F9FA';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px' }}>⚡</span>
                <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>&lt;800MS LIVE</span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#202124' }}>Talk to Maya Live</div>
              <div style={{ fontSize: '11px', color: '#5F6368', lineHeight: 1.4 }}>
                Real-time speech-to-speech with barge-in interruption.
              </div>
            </div>

            {/* Preset 4: ClickHouse Telemetry */}
            <div
              onClick={() => onNavigate('evolution')}
              style={{
                backgroundColor: '#F8F9FA',
                border: '1px solid #DADCE0',
                borderRadius: '12px',
                padding: '16px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#137333';
                e.currentTarget.style.backgroundColor = '#F6FCF8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#DADCE0';
                e.currentTarget.style.backgroundColor = '#F8F9FA';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px' }}>📊</span>
                <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>MCP BRIDGE</span>
              </div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#202124' }}>ClickHouse Analytics</div>
              <div style={{ fontSize: '11px', color: '#5F6368', lineHeight: 1.4 }}>
                Query telemetry via Model Context Protocol (MCP).
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. THE ARCHITECTURAL SHIFT: Problem vs Solution */}
      <section style={{
        backgroundColor: '#F8F9FA',
        padding: '60px 32px',
        borderBottom: '1px solid #DADCE0'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <span className="badge-neon badge-primary" style={{ padding: '3px 12px', fontSize: '10px' }}>
              THE ARCHITECTURAL DIFFERENCE
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 600, fontFamily: 'Google Sans, sans-serif', marginTop: '10px', color: '#202124' }}>
              Why AvatarOS is Not Another AI Video Generator
            </h2>
            <p style={{ fontSize: '14.5px', color: '#5F6368', marginTop: '6px' }}>
              Traditional generative AI treats video as disposable pixels. AvatarOS treats digital actors as permanent enterprise software assets.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* The Old Way */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #FAD2CF',
              borderRadius: '16px',
              padding: '28px',
              boxShadow: '0 1px 3px rgba(60,64,67,0.08)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <AlertTriangle size={20} color="#C5221F" />
                <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#C5221F' }}>
                  Traditional AI Video Generators
                </h3>
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px', color: '#5F6368', padding: 0, margin: 0 }}>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#C5221F', fontWeight: 700 }}>✕</span>
                  <span><strong>Disposable one-off clips:</strong> Likeness, facial geometry, and voice drift across every single generation prompt.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#C5221F', fontWeight: 700 }}>✕</span>
                  <span><strong>AI Hallucinations:</strong> Actors routinely state unsupported marketing claims with zero citation grounding.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#C5221F', fontWeight: 700 }}>✕</span>
                  <span><strong>Zero legal rights protection:</strong> Likeness and voice used without cryptographically verifiable consent boundaries.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#C5221F', fontWeight: 700 }}>✕</span>
                  <span><strong>Disconnected offline pipeline:</strong> Inability to participate in live customer conversations or webinar Q&amp;A.</span>
                </li>
              </ul>
            </div>

            {/* The AvatarOS Breakthrough */}
            <div style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #CEEAD6',
              borderRadius: '16px',
              padding: '28px',
              boxShadow: '0 1px 3px rgba(60,64,67,0.08)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <CheckCircle2 size={20} color="#137333" />
                <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#137333' }}>
                  The AvatarOS Autonomous Studio
                </h3>
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px', color: '#202124', padding: 0, margin: 0 }}>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#137333', fontWeight: 700 }}>✓</span>
                  <span><strong>Digital DNA Persistence:</strong> ArcFace 512-d biometric face vector and voice model sealed under versioned hashes.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#137333', fontWeight: 700 }}>✓</span>
                  <span><strong>Forced Evidence Gate:</strong> Every statement verified against documentation. Ungrounded claims like '3x faster' blocked instantly.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#137333', fontWeight: 700 }}>✓</span>
                  <span><strong>Ed25519 Likeness Rights:</strong> Signed cryptographic consent bounds permissible topics, registers, and expiry.</span>
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <span style={{ color: '#137333', fontWeight: 700 }}>✓</span>
                  <span><strong>Dual Studio &amp; Realtime Live:</strong> Switch seamlessly from directed 4K video ads to low-latency Gemini Live conversation.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 4. THE 4-STAGE PIPELINE: Clear, Understandable Architecture */}
      <section style={{ padding: '60px 32px', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <span className="badge-neon badge-primary" style={{ padding: '3px 12px', fontSize: '10px' }}>
            HOW IT WORKS
          </span>
          <h2 style={{ fontSize: '32px', fontWeight: 600, fontFamily: 'Google Sans, sans-serif', marginTop: '10px', color: '#202124' }}>
            The 4-Stage Autonomous Pipeline
          </h2>
          <p style={{ fontSize: '14px', color: '#5F6368', marginTop: '6px' }}>
            From high-level creative brief to broadcast-ready video with zero human intervention.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
          {/* Stage 1 */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #DADCE0',
            borderRadius: '16px',
            padding: '24px',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#E8F0FE',
              color: '#1A73E8',
              fontWeight: 700,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              1
            </div>
            <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#202124' }}>Cast &amp; Legal Consent</h4>
            <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5 }}>
              Select actor from Digital Cast. Engine binds ArcFace 512-d embeddings and verifies cryptographic Ed25519 likeness rights.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
              <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>ED25519 SIGNED</span>
            </div>
          </div>

          {/* Stage 2 */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #DADCE0',
            borderRadius: '16px',
            padding: '24px',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#FEF7E0',
              color: '#B06000',
              fontWeight: 700,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              2
            </div>
            <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#202124' }}>Grounded Research</h4>
            <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5 }}>
              Research Agent executes hybrid BM25 + dense vector queries on technical documentation to extract verified claims and evidence citations.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
              <span className="badge-neon badge-amber" style={{ fontSize: '9px' }}>HYBRID BM25</span>
            </div>
          </div>

          {/* Stage 3 */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #DADCE0',
            borderRadius: '16px',
            padding: '24px',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#E6F4EA',
              color: '#137333',
              fontWeight: 700,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              3
            </div>
            <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#202124' }}>Direct &amp; Critic Loop</h4>
            <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5 }}>
              Director Agent structures multi-scene emotion, energy, and camera angles. Critic Agent scores script fidelity and enforces character persona.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
              <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>ADVERSARIAL CRITIC</span>
            </div>
          </div>

          {/* Stage 4 */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #DADCE0',
            borderRadius: '16px',
            padding: '24px',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#FCE8E6',
              color: '#D93025',
              fontWeight: 700,
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              4
            </div>
            <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#202124' }}>Guardian &amp; Provenance</h4>
            <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5 }}>
              Multimodal Guardian inspects rendered frames against face biometrics and voice timbre. Publication Gate attaches C2PA tamper-evident manifests.
            </p>
            <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
              <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>C2PA MANIFEST</span>
            </div>
          </div>
        </div>
      </section>

      {/* 5. MULTI-PAGE WORKSPACES: 6 Clickable System Pillars */}
      <section style={{
        backgroundColor: '#F8F9FA',
        padding: '60px 32px',
        borderTop: '1px solid #DADCE0',
        borderBottom: '1px solid #DADCE0'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <span className="badge-neon badge-primary" style={{ padding: '3px 12px', fontSize: '10px' }}>
              MULTI-PAGE EXPLORATION
            </span>
            <h2 style={{ fontSize: '32px', fontWeight: 600, fontFamily: 'Google Sans, sans-serif', marginTop: '10px', color: '#202124' }}>
              Explore the System Workspaces
            </h2>
            <p style={{ fontSize: '14px', color: '#5F6368', marginTop: '6px' }}>
              Click into any workspace to inspect the autonomous multi-agent infrastructure in real time.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
            
            {/* Card 1: Autonomous Studio */}
            <div
              className="glass-panel"
              onClick={() => onNavigate('studio')}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#E8F0FE', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Film size={18} color="#1A73E8" />
                </div>
                <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>STUDIO MODE</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#202124' }}>Autonomous Directed Studio</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                Submit a high-level brief. The 9-agent DAG orchestrates research, drafting, adversarial critique, shot choreographing, and multimodal rendering.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: '#1A73E8' }}>
                <span>Open Studio Control Plane</span>
                <ArrowRight size={13} />
              </div>
            </div>

            {/* Card 2: Live Mode */}
            <div
              className="glass-panel"
              onClick={() => onNavigate('live')}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#E8F0FE', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Zap size={18} color="#1A73E8" />
                </div>
                <span className="badge-neon badge-amber" style={{ fontSize: '10px' }}>REALTIME LIVE</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#202124' }}>Real-Time Conversational Avatar</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                Speak directly with Maya using low-latency bidirectional audio with sub-800ms latency, user barge-in interruption, and isolated memory.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: '#1A73E8' }}>
                <span>Launch Live Audio Session</span>
                <ArrowRight size={13} />
              </div>
            </div>

            {/* Card 3: Analytics & ClickHouse */}
            <div
              className="glass-panel"
              onClick={() => onNavigate('evolution')}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#E6F4EA', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Database size={18} color="#137333" />
                </div>
                <span className="badge-neon badge-emerald" style={{ fontSize: '10px' }}>CLICKHOUSE MCP</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#202124' }}>ClickHouse Telemetry &amp; MCP</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                Autonomous closed-loop learning. The Evolution Agent queries ClickHouse telemetry via Model Context Protocol (MCP) to optimize hook strategies.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: '#137333' }}>
                <span>Inspect Governed MCP Bridge</span>
                <ArrowRight size={13} />
              </div>
            </div>

            {/* Card 4: Knowledge Vault */}
            <div
              className="glass-panel"
              onClick={() => onNavigate('knowledge')}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#FEF7E0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FileSearch size={18} color="#B06000" />
                </div>
                <span className="badge-neon badge-amber" style={{ fontSize: '10px' }}>HYBRID BM25</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#202124' }}>Grounded Knowledge &amp; Citations</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                Inspect indexed benchmark PDFs and specifications. Research agents use hybrid sparse and dense vector search to pull incontrovertible facts.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: '#B06000' }}>
                <span>Browse Knowledge Base</span>
                <ArrowRight size={13} />
              </div>
            </div>

            {/* Card 5: Digital DNA & Cast */}
            <div
              className="glass-panel"
              onClick={onInspectDna}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#E4F7FB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Dna size={18} color="#007B83" />
                </div>
                <span className="badge-neon badge-cyan" style={{ fontSize: '10px' }}>DNA VAULT</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#202124' }}>Digital DNA &amp; Likeness Consent</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                Inspect Maya v1.7.0's ArcFace 512-d face vector, voice timbre parameters, and cryptographic Ed25519 legal authorization agreements.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 600, color: '#007B83' }}>
                <span>Inspect DNA Manifest</span>
                <ArrowRight size={13} />
              </div>
            </div>

            {/* Card 6: Cinematic Judge Tour */}
            <div
              className="glass-panel"
              onClick={onOpenJudgeMode}
              style={{ padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column', gap: '12px', border: '1px solid #1A73E8', backgroundColor: '#F8FBFF' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: '#1A73E8', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Award size={18} color="#FFFFFF" />
                </div>
                <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>JUDGE SPECIAL</span>
              </div>
              <h3 style={{ fontSize: '17px', fontWeight: 600, color: '#1A73E8' }}>Cinematic Judge Tour (6 Chapters)</h3>
              <p style={{ fontSize: '12px', color: '#5F6368', lineHeight: 1.5, flex: 1 }}>
                A full widescreen interactive walkthrough covering the thesis, autonomous DAG, safety gates, Gemini Live, ClickHouse MCP, and final scorecard.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', fontWeight: 700, color: '#1A73E8' }}>
                <span>Start Cinematic Walkthrough</span>
                <ArrowRight size={13} />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 6. TECHNOLOGY STACK & ENTERPRISE TRUST STRIP */}
      <section style={{ padding: '40px 32px', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #1A73E8 0%, #174EA6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontWeight: 700,
              fontSize: '13px'
            }}>
              A
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#202124' }}>
                Enterprise Autonomous Architecture
              </div>
              <div style={{ fontSize: '11px', color: '#5F6368' }}>
                ArcFace 512-d Identity • Ed25519 Rights • 9-Agent DAG Orchestrator • Realtime Audio
              </div>
            </div>
          </div>

          {/* Partner Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <span style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              border: '1px solid #DADCE0',
              backgroundColor: '#FFFFFF',
              fontSize: '11px',
              color: '#5F6368',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Database size={12} color="#137333" />
              ClickHouse Cloud OLAP
            </span>

            <span style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              border: '1px solid #DADCE0',
              backgroundColor: '#FFFFFF',
              fontSize: '11px',
              color: '#5F6368',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <ShieldCheck size={12} color="#1A73E8" />
              C2PA Content Credentials
            </span>

            <span style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              border: '1px solid #DADCE0',
              backgroundColor: '#FFFFFF',
              fontSize: '11px',
              color: '#5F6368',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <Cpu size={12} color="#B06000" />
              Model Context Protocol (MCP)
            </span>
          </div>
        </div>
      </section>

      {/* 7. FOOTER */}
      <footer style={{
        backgroundColor: '#FFFFFF',
        borderTop: '1px solid #DADCE0',
        padding: '24px 32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '12px',
        color: '#5F6368',
        marginTop: 'auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: '#1A73E8', fontWeight: 700 }}>AvatarOS</span>
          <span>•</span>
          <span>Autonomous Digital Human Operating System</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span>C2PA Content Credentials Signed</span>
          <span>•</span>
          <span>Sub-800ms Realtime Voice</span>
          <span>•</span>
          <span>Cryptographic Rights Sealed</span>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
