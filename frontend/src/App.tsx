import React, { useState, useEffect } from 'react';
import {
  Home, Film, Sparkles, MessageSquare, Database, Terminal, Shield, RefreshCw,
  Play, CheckCircle2, AlertTriangle, Layers, Dna, UploadCloud, BookOpen, Globe, Cloud, Search, Award
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { HomePage } from './components/HomePage';
import { DigitalCast } from './components/DigitalCast';
import { LiveStage } from './components/LiveStage';
import { AgentActivity } from './components/AgentActivity';
import { ProductionTimeline } from './components/ProductionTimeline';
import { LiveModeChat } from './components/LiveModeChat';
import { ClickHouseEvolution } from './components/ClickHouseEvolution';
import { KnowledgeRetrieval } from './components/KnowledgeRetrieval';
import { DemoGuide } from './components/DemoGuide';
import { DnaModal } from './components/DnaModal';
import { CompilerModal } from './components/CompilerModal';
import { ProviderMatrixModal } from './components/ProviderMatrixModal';
import { CinematicJudgeMode } from './components/CinematicJudgeMode';

export const App: React.FC = () => {
  const [cast, setCast] = useState<any[]>([]);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string>('maya');
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'hi'>('en');
  const [selectedRegister, setSelectedRegister] = useState<string>('technical');
  const getInitialPage = (): 'home' | 'studio' | 'live' | 'evolution' | 'knowledge' => {
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace('#', '');
      if (['home', 'studio', 'live', 'evolution', 'knowledge'].includes(hash)) {
        return hash as any;
      }
    }
    return 'home';
  };

  const [viewMode, setViewMode] = useState<'home' | 'studio' | 'live' | 'evolution' | 'knowledge'>(getInitialPage());
  const [showJudgeMode, setShowJudgeMode] = useState(false);
  const [commandInput, setCommandInput] = useState<string>(
    "Create a 60-second product launch for Indian developers. Research our documentation first. Do not make unsupported claims. Produce English and Hindi versions."
  );

  const navigateTo = (page: 'home' | 'studio' | 'live' | 'evolution' | 'knowledge') => {
    setViewMode(page);
    if (typeof window !== 'undefined') {
      window.location.hash = page;
    }
  };

  const [campaignData, setCampaignData] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeSceneNo, setActiveSceneNo] = useState<number>(1);
  const [demoStep, setDemoStep] = useState<number>(2);

  // Modals
  const [dnaModalCharId, setDnaModalCharId] = useState<string | null>(null);
  const [showCompilerModal, setShowCompilerModal] = useState(false);
  const [showProviderMatrixModal, setShowProviderMatrixModal] = useState(false);

  useEffect(() => {
    fetch('/api/cast')
      .then((r) => r.json())
      .then((data) => setCast(data))
      .catch(console.error);

    // Initial autonomous production run to populate studio stage in background
    runProduction({ injectClaimFail: false, injectEmotionFail: false, simulateRightsFail: false });

    // Sync hash changes with viewMode
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      if (['home', 'studio', 'live', 'evolution', 'knowledge'].includes(hash)) {
        setViewMode(hash as any);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const runProduction = async (opts: {
    injectClaimFail?: boolean;
    injectEmotionFail?: boolean;
    simulateRightsFail?: boolean;
    customBrief?: string;
  } = {}) => {
    setIsExecuting(true);
    try {
      const res = await fetch('/api/production/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: selectedCharacterId,
          brief: opts.customBrief || commandInput,
          campaign_id: "titan_laptop_india_devs",
          language: selectedLanguage,
          register: selectedRegister,
          inject_claim_failure: opts.injectClaimFail || false,
          inject_emotion_failure: opts.injectEmotionFail || false,
          simulate_rights_failure: opts.simulateRightsFail || false
        })
      });
      const data = await res.json();
      setCampaignData({
        run_id: data.run_id,
        trace_id: data.trace_id,
        character: cast.find((c) => c.character_id === selectedCharacterId) || { name: "Maya", version: "v1.7.0" },
        research: data.research_result,
        claims: data.claims_result,
        script: data.script_result,
        critic_report: data.critic_result,
        director_plan: data.director_result,
        performance_plan: data.performance_result,
        guardian_report: data.guardian_result,
        publish_result: data.publish_result,
        hindi_production: data.hindi_production,
        repurposed_clips: data.repurposed_clips,
        master_video_url: data.master_video_url,
        media_sha256: data.media_sha256,
        scorecard: data.scorecard,
        failure_ux: data.failure_ux,
        stages: data.stages
      });
    } catch (e) {
      console.error("Production execution error:", e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleDemoClaimBlock = async () => {
    setIsExecuting(true);
    try {
      const res = await fetch('/api/production/demo/claim-block', { method: 'POST' });
      const data = await res.json();
      setCampaignData({
        run_id: data.run_id,
        trace_id: data.trace_id,
        character: cast.find((c) => c.character_id === selectedCharacterId) || { name: "Maya", version: "v1.7.0" },
        research: data.research_result,
        claims: data.claims_result,
        script: data.script_result,
        critic_report: data.critic_result,
        director_plan: data.director_result,
        performance_plan: data.performance_result,
        guardian_report: data.guardian_result,
        publish_result: data.publish_result,
        scorecard: data.scorecard,
        failure_ux: data.failure_ux,
        stages: data.stages
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleDemoGuardianFailure = async () => {
    setIsExecuting(true);
    try {
      const res = await fetch('/api/production/demo/guardian-failure', { method: 'POST' });
      const data = await res.json();
      setCampaignData({
        run_id: data.run_id,
        trace_id: data.trace_id,
        character: cast.find((c) => c.character_id === selectedCharacterId) || { name: "Maya", version: "v1.7.0" },
        research: data.research_result,
        claims: data.claims_result,
        script: data.script_result,
        critic_report: data.critic_result,
        director_plan: data.director_result,
        performance_plan: data.performance_result,
        guardian_report: data.guardian_result,
        publish_result: data.publish_result,
        scorecard: data.scorecard,
        failure_ux: data.failure_ux,
        stages: data.stages
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleDemoRightsBlock = async () => {
    setIsExecuting(true);
    try {
      const res = await fetch('/api/production/demo/rights-block', { method: 'POST' });
      const data = await res.json();
      setCampaignData({
        run_id: data.run_id,
        trace_id: data.trace_id,
        character: cast.find((c) => c.character_id === selectedCharacterId) || { name: "Maya", version: "v1.7.0" },
        research: data.research_result,
        claims: data.claims_result,
        script: data.script_result,
        critic_report: data.critic_result,
        director_plan: data.director_result,
        performance_plan: data.performance_result,
        guardian_report: data.guardian_result,
        publish_result: data.publish_result,
        scorecard: data.scorecard,
        failure_ux: data.failure_ux,
        stages: data.stages
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleResolveClaim = async () => {
    try {
      await fetch('/api/campaign/claim/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          claim_id: "claim_fail_3x",
          evidence_document: "titan_benchmarks_mlperf_v2.pdf"
        })
      });
      // Re-run production cleanly to show publication unblocked
      runProduction({ injectClaimFail: false, injectEmotionFail: false });
    } catch (e) {
      console.error(e);
    }
  };

  const handleReworkScene = async () => {
    try {
      await fetch('/api/campaign/scene/rework?scene_no=4', { method: 'POST' });
      // Re-run clean production
      runProduction({ injectClaimFail: false, injectEmotionFail: false });
    } catch (e) {
      console.error(e);
    }
  };

  const handleLiveHandoffToStudio = (draftBrief: string) => {
    setCommandInput(draftBrief);
    setViewMode('studio');
  };

  const currentCharacter = cast.find((c) => c.character_id === selectedCharacterId) || {
    name: "Maya",
    version: "v1.7.0"
  };

  const activeShot = campaignData?.director_plan?.shots?.find((s: any) => s.scene_no === activeSceneNo) || {
    target_emotion: "confident",
    emotional_intensity: 0.78
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--color-background)' }}>
      {/* Official Google 4-Color Accent Line */}
      <div className="google-accent-line" />
      
      {/* Top Navigation Bar */}
      <header style={{
        height: '56px',
        borderBottom: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--color-surface)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        flexShrink: 0
      }}>
        {/* Brand */}
        <div
          onClick={() => navigateTo('home')}
          style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', userSelect: 'none' }}
          title="Go to AvatarOS Home"
        >
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #1A73E8 0%, #174EA6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 800,
            fontSize: '16px',
            boxShadow: '0 2px 8px rgba(26, 115, 232, 0.4)'
          }}>
            A
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '16px', fontWeight: 600, letterSpacing: '-0.2px', fontFamily: 'Google Sans, -apple-system, sans-serif' }}>
                Avatar<span style={{ color: 'var(--color-primary)' }}>OS</span>
              </h1>
              <span className="badge-neon badge-primary" style={{ fontSize: '9px', padding: '1px 8px' }}>
                ENTERPRISE
              </span>
            </div>
            <p style={{ fontSize: '10.5px', color: 'var(--text-muted)' }}>
              Autonomous Digital Human Operating System
            </p>
          </div>
        </div>

        {/* View Mode Switcher */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--color-background)',
          padding: '3px',
          borderRadius: 'var(--radius-full)',
          border: '1px solid var(--border-subtle)',
          gap: '4px'
        }}>
          <button
            className="btn"
            onClick={() => navigateTo('home')}
            style={{
              padding: '6px 16px',
              fontSize: '12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: viewMode === 'home' ? 'var(--color-primary)' : 'transparent',
              color: viewMode === 'home' ? 'var(--color-on-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'home' ? 600 : 500
            }}
          >
            <Home size={13} />
            Home
          </button>
          <button
            className="btn"
            onClick={() => navigateTo('studio')}
            style={{
              padding: '6px 16px',
              fontSize: '12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: viewMode === 'studio' ? 'var(--color-primary)' : 'transparent',
              color: viewMode === 'studio' ? 'var(--color-on-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'studio' ? 600 : 500
            }}
          >
            <Film size={13} />
            Studio Mode
          </button>
          <button
            className="btn"
            onClick={() => navigateTo('live')}
            style={{
              padding: '6px 16px',
              fontSize: '12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: viewMode === 'live' ? 'var(--color-primary)' : 'transparent',
              color: viewMode === 'live' ? 'var(--color-on-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'live' ? 600 : 500
            }}
          >
            <MessageSquare size={13} />
            Live Mode (Realtime)
          </button>
          <button
            className="btn"
            onClick={() => navigateTo('evolution')}
            style={{
              padding: '6px 16px',
              fontSize: '12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: viewMode === 'evolution' ? 'var(--color-primary)' : 'transparent',
              color: viewMode === 'evolution' ? 'var(--color-on-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'evolution' ? 600 : 500
            }}
          >
            <Database size={13} />
            Analytics &amp; ClickHouse
          </button>
          <button
            className="btn"
            onClick={() => navigateTo('knowledge')}
            style={{
              padding: '6px 16px',
              fontSize: '12px',
              borderRadius: 'var(--radius-full)',
              backgroundColor: viewMode === 'knowledge' ? 'var(--color-primary)' : 'transparent',
              color: viewMode === 'knowledge' ? 'var(--color-on-primary)' : 'var(--text-muted)',
              fontWeight: viewMode === 'knowledge' ? 600 : 500
            }}
          >
            <BookOpen size={13} />
            Knowledge &amp; Evidence
          </button>
        </div>

        {/* Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '11px' }}>
          <button
            className="btn btn-secondary"
            style={{ padding: '5px 12px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '6px', borderRadius: 'var(--radius-full)' }}
            onClick={() => setShowProviderMatrixModal(true)}
          >
            <Cloud size={13} color="var(--color-primary)" />
            Cloud Infrastructure (11/11 Active)
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div className="status-dot active" />
            <span style={{ color: 'var(--text-secondary)' }}>{currentCharacter.name} {currentCharacter.version} (DNA Sealed)</span>
          </div>
          <button
            className="btn btn-secondary"
            style={{ padding: '5px 12px', fontSize: '11px', borderRadius: 'var(--radius-full)' }}
            onClick={() => setDnaModalCharId(selectedCharacterId)}
          >
            <Dna size={13} color="var(--color-primary)" />
            DNA Inspector
          </button>
          <button
            className="btn judge-mode-btn"
            style={{
              padding: '6px 14px',
              fontSize: '11px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              borderRadius: 'var(--radius-full)',
              background: 'linear-gradient(135deg, #1A73E8 0%, #174EA6 100%)',
              color: '#FFFFFF',
              boxShadow: '0 2px 8px rgba(26, 115, 232, 0.4)'
            }}
            onClick={() => setShowJudgeMode(true)}
            title="Open Cinematic Judge Walkthrough"
          >
            <Award size={14} color="#FFD700" />
            <span>JUDGE MODE</span>
            <span style={{ backgroundColor: 'rgba(255,255,255,0.25)', padding: '1px 6px', borderRadius: '9999px', fontSize: '9px' }}>
              TOUR
            </span>
          </button>
        </div>
      </header>

      {/* Google Search-Style Production Creation Bar */}
      {viewMode === 'studio' && (
        <div style={{
          padding: '12px 24px',
          backgroundColor: 'var(--color-background)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          {/* Main Prompt Bar Container */}
          <div className="google-prompt-bar" style={{ flex: 1 }}>
            <Sparkles size={16} color="var(--google-blue)" style={{ marginRight: '8px', flexShrink: 0 }} />
            
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              placeholder="Enter production brief (character, goal, audience, language)..."
              style={{
                width: '100%',
                backgroundColor: 'transparent',
                border: 'none',
                color: 'var(--color-neutral)',
                fontSize: '13px',
                outline: 'none',
                fontFamily: 'Roboto, sans-serif'
              }}
            />

            {/* Language & Register Controls Embedded */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', paddingRight: '4px', flexShrink: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Globe size={13} color="var(--color-primary)" />
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value as 'en' | 'hi')}
                  style={{
                    backgroundColor: 'var(--color-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-full)',
                    padding: '4px 8px',
                    color: 'var(--color-neutral)',
                    fontSize: '11px',
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="en">EN (Indian)</option>
                  <option value="hi">HI (Hindi)</option>
                </select>
              </div>

              <select
                value={selectedRegister}
                onChange={(e) => setSelectedRegister(e.target.value)}
                style={{
                  backgroundColor: 'var(--color-surface-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-full)',
                  padding: '4px 8px',
                  color: 'var(--color-neutral)',
                  fontSize: '11px',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="technical">Register: Technical</option>
                <option value="conversational">Register: Conversational</option>
                <option value="executive">Register: Executive</option>
              </select>
            </div>
          </div>

          {/* CREATE PRODUCTION Action Button */}
          <button
            className="btn btn-primary"
            onClick={() => runProduction({})}
            disabled={isExecuting}
            style={{ padding: '8px 22px', fontSize: '13px', fontWeight: 600, flexShrink: 0 }}
          >
            {isExecuting ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
            CREATE PRODUCTION
          </button>
        </div>
      )}

      {/* Main Workspace Body with Framer Motion transitions */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', position: 'relative' }}>
        <AnimatePresence mode="wait">
          {viewMode === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', overflow: 'hidden' }}
            >
              <HomePage
                onNavigate={(page) => {
                  if (page === 'cast') {
                    navigateTo('studio');
                  } else {
                    navigateTo(page);
                  }
                }}
                onOpenJudgeMode={() => setShowJudgeMode(true)}
                onInspectDna={() => setDnaModalCharId(selectedCharacterId || 'maya')}
                onLaunchPreset={(brief) => {
                  setCommandInput(brief);
                  navigateTo('studio');
                  runProduction({ customBrief: brief });
                }}
                onTriggerClaimDemo={() => {
                  navigateTo('studio');
                  handleDemoClaimBlock();
                }}
              />
            </motion.div>
          )}

          {viewMode === 'studio' && (
            <motion.div
              key="studio"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', overflow: 'hidden' }}
            >
              <DigitalCast
                cast={cast}
                selectedId={selectedCharacterId}
                onSelect={setSelectedCharacterId}
                onOpenCompiler={() => setShowCompilerModal(true)}
                onOpenDnaModal={(id) => setDnaModalCharId(id)}
              />

              <LiveStage
                videoUrl={campaignData?.master_video_url || "/media/master_video_en.mp4"}
                hindiVideoUrl={campaignData?.hindi_production?.video_url}
                characterName={currentCharacter.name}
                characterVersion={currentCharacter.version}
                activeSceneNo={activeSceneNo}
                targetEmotion={activeShot.target_emotion}
                energy={activeShot.emotional_intensity}
                c2paManifestHash={campaignData?.publish_result?.provenance?.c2pa_manifest_hash}
                mediaSha256={campaignData?.media_sha256}
                repurposedClips={campaignData?.repurposed_clips}
              />

              <AgentActivity
                campaignData={campaignData}
                onTriggerClaimFailure={handleDemoClaimBlock}
                onResolveClaim={handleResolveClaim}
                onTriggerEmotionFailure={handleDemoGuardianFailure}
                onTriggerRightsFailure={handleDemoRightsBlock}
                onReworkScene={handleReworkScene}
                isExecuting={isExecuting}
              />
            </motion.div>
          )}

          {viewMode === 'live' && (
            <motion.div
              key="live"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', overflow: 'hidden' }}
            >
              <LiveModeChat onHandoffToStudio={handleLiveHandoffToStudio} />
            </motion.div>
          )}

          {viewMode === 'evolution' && (
            <motion.div
              key="evolution"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', overflow: 'hidden' }}
            >
              <ClickHouseEvolution />
            </motion.div>
          )}

          {viewMode === 'knowledge' && (
            <motion.div
              key="knowledge"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.2 }}
              style={{ flex: 1, display: 'flex', overflow: 'hidden' }}
            >
              <KnowledgeRetrieval />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom Production Timeline (Only in Studio Mode) */}
      {viewMode === 'studio' && (
        <ProductionTimeline
          shots={campaignData?.director_plan?.shots || []}
          activeSceneNo={activeSceneNo}
          onSelectScene={setActiveSceneNo}
          failedScenes={campaignData?.guardian_report?.failed_scenes}
          isBlocked={campaignData?.publish_result?.status === 'BLOCKED'}
        />
      )}

      {/* Floating 9-Step Demo Walkthrough Guide */}
      <DemoGuide
        currentStep={demoStep}
        onSelectStep={(step) => {
          setDemoStep(step);
          if (step === 1) setDnaModalCharId('maya');
          if (step === 2) navigateTo('studio');
          if (step === 3) navigateTo('studio');
          if (step === 6) navigateTo('studio');
          if (step === 7) navigateTo('live');
          if (step === 8 || step === 9) navigateTo('evolution');
        }}
        onExecuteFullRun={() => {
          navigateTo('studio');
          runProduction({});
        }}
        onTriggerClaimFail={handleDemoClaimBlock}
        onResolveClaim={handleResolveClaim}
        onTriggerEmotionFail={handleDemoGuardianFailure}
        onReworkScene={handleReworkScene}
        onOpenLiveMode={() => navigateTo('live')}
        onOpenEvolution={() => navigateTo('evolution')}
      />

      {/* Modals */}
      {dnaModalCharId && (
        <DnaModal characterId={dnaModalCharId} onClose={() => setDnaModalCharId(null)} />
      )}

      {showCompilerModal && (
        <CompilerModal onClose={() => setShowCompilerModal(false)} />
      )}

      {showProviderMatrixModal && (
        <ProviderMatrixModal isOpen={showProviderMatrixModal} onClose={() => setShowProviderMatrixModal(false)} />
      )}

      {showJudgeMode && (
        <CinematicJudgeMode
          isOpen={showJudgeMode}
          onClose={() => setShowJudgeMode(false)}
          onInspectDna={() => {
            setShowJudgeMode(false);
            setDnaModalCharId('maya');
          }}
          onRunProduction={() => {
            setShowJudgeMode(false);
            navigateTo('studio');
            runProduction({});
          }}
          onTriggerClaimFail={() => {
            setShowJudgeMode(false);
            navigateTo('studio');
            handleDemoClaimBlock();
          }}
          onResolveClaim={() => {
            setShowJudgeMode(false);
            navigateTo('studio');
            handleResolveClaim();
          }}
          onOpenLiveMode={() => {
            setShowJudgeMode(false);
            navigateTo('live');
          }}
          onOpenEvolution={() => {
            setShowJudgeMode(false);
            navigateTo('evolution');
          }}
        />
      )}
    </div>
  );
};

export default App;
