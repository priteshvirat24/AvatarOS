import React, { useState, useEffect } from 'react';
import {
  Film, Sparkles, MessageSquare, Database, Terminal, Shield, RefreshCw,
  Play, CheckCircle2, AlertTriangle, Layers, Dna, UploadCloud, BookOpen, Globe, Cloud
} from 'lucide-react';

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

export const App: React.FC = () => {
  const [cast, setCast] = useState<any[]>([]);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string>('maya');
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'hi'>('en');
  const [selectedRegister, setSelectedRegister] = useState<string>('technical');
  const [viewMode, setViewMode] = useState<'studio' | 'live' | 'evolution' | 'knowledge'>('studio');
  const [commandInput, setCommandInput] = useState<string>(
    "Create a 60-second product launch for Indian developers. Research our documentation first. Do not make unsupported claims. Produce English and Hindi versions."
  );

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

    // Initial autonomous production run to populate studio stage
    runProduction({ injectClaimFail: false, injectEmotionFail: false, simulateRightsFail: false });
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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      
      {/* Top Navigation Bar */}
      <header style={{
        height: '56px',
        borderBottom: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-darkest)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        flexShrink: 0
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '6px',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 900,
            fontSize: '15px'
          }}>
            A
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <h1 style={{ fontSize: '15px', fontWeight: 900, letterSpacing: '0.5px' }}>
                AVATAR<span style={{ color: 'var(--primary-light)' }}>OS</span>
              </h1>
              <span className="badge-neon badge-primary" style={{ fontSize: '9px', padding: '0 5px' }}>AUTONOMOUS STUDIO</span>
            </div>
            <p style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
              Create a digital actor once. Direct them forever.
            </p>
          </div>
        </div>

        {/* View Mode Switcher */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--bg-surface)',
          padding: '3px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
          gap: '4px'
        }}>
          <button
            className="btn"
            onClick={() => setViewMode('studio')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              backgroundColor: viewMode === 'studio' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'studio' ? 'white' : 'var(--text-muted)'
            }}
          >
            <Film size={13} />
            Studio Mode
          </button>
          <button
            className="btn"
            onClick={() => setViewMode('live')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              backgroundColor: viewMode === 'live' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'live' ? 'white' : 'var(--text-muted)'
            }}
          >
            <MessageSquare size={13} />
            Live Mode
          </button>
          <button
            className="btn"
            onClick={() => setViewMode('evolution')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              backgroundColor: viewMode === 'evolution' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'evolution' ? 'white' : 'var(--text-muted)'
            }}
          >
            <Database size={13} />
            ClickHouse &amp; MCP
          </button>
          <button
            className="btn"
            onClick={() => setViewMode('knowledge')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              backgroundColor: viewMode === 'knowledge' ? 'var(--primary)' : 'transparent',
              color: viewMode === 'knowledge' ? 'white' : 'var(--text-muted)'
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
            style={{ padding: '4px 8px', fontSize: '10px', display: 'flex', alignItems: 'center', gap: '4px', borderColor: 'rgba(99, 102, 241, 0.4)', color: 'var(--primary-light)' }}
            onClick={() => setShowProviderMatrixModal(true)}
          >
            <Cloud size={12} />
            Providers &amp; Cloud (11/11)
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div className="status-dot active" />
            <span style={{ color: 'var(--text-secondary)' }}>{currentCharacter.name} {currentCharacter.version} (DNA Locked)</span>
          </div>
          <button
            className="btn btn-secondary"
            style={{ padding: '4px 8px', fontSize: '10px' }}
            onClick={() => setDnaModalCharId(selectedCharacterId)}
          >
            <Dna size={12} />
            DNA Inspector
          </button>
        </div>
      </header>

      {/* Section 3: Single-Action Production Creation Bar */}
      {viewMode === 'studio' && (
        <div style={{
          padding: '10px 20px',
          backgroundColor: 'var(--bg-base)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          {/* Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Globe size={13} color="var(--primary-light)" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value as 'en' | 'hi')}
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 8px',
                color: 'white',
                fontSize: '11px',
                outline: 'none'
              }}
            >
              <option value="en">English (EN)</option>
              <option value="hi">Hindi (HI)</option>
            </select>
          </div>

          {/* Register Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <select
              value={selectedRegister}
              onChange={(e) => setSelectedRegister(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '5px 8px',
                color: 'white',
                fontSize: '11px',
                outline: 'none'
              }}
            >
              <option value="technical">Register: Technical</option>
              <option value="conversational">Register: Conversational</option>
              <option value="executive">Register: Executive</option>
            </select>
          </div>

          {/* Input Brief */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', position: 'relative' }}>
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              placeholder="Enter production brief (character, goal, audience, language)..."
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '7px 12px',
                color: 'white',
                fontSize: '12px',
                outline: 'none'
              }}
            />
          </div>

          {/* CREATE PRODUCTION Action Button */}
          <button
            className="btn btn-primary"
            onClick={() => runProduction({})}
            disabled={isExecuting}
            style={{ padding: '7px 18px', fontSize: '12px', fontWeight: 700 }}
          >
            {isExecuting ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
            CREATE PRODUCTION
          </button>
        </div>
      )}

      {/* Main Workspace Body */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {viewMode === 'studio' && (
          <>
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
          </>
        )}

        {viewMode === 'live' && (
          <LiveModeChat onHandoffToStudio={handleLiveHandoffToStudio} />
        )}

        {viewMode === 'evolution' && (
          <ClickHouseEvolution />
        )}

        {viewMode === 'knowledge' && (
          <KnowledgeRetrieval />
        )}
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
          if (step === 2) setViewMode('studio');
          if (step === 3) setViewMode('studio');
          if (step === 6) setViewMode('studio');
          if (step === 7) setViewMode('live');
          if (step === 8 || step === 9) setViewMode('evolution');
        }}
        onExecuteFullRun={() => {
          setViewMode('studio');
          runProduction({});
        }}
        onTriggerClaimFail={handleDemoClaimBlock}
        onResolveClaim={handleResolveClaim}
        onTriggerEmotionFail={handleDemoGuardianFailure}
        onReworkScene={handleReworkScene}
        onOpenLiveMode={() => setViewMode('live')}
        onOpenEvolution={() => setViewMode('evolution')}
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
    </div>
  );
};

export default App;
