import React, { useState } from 'react';
import { PlayCircle, CheckCircle2, ChevronRight, Sparkles, AlertTriangle, ShieldCheck, Database, Film, MessageSquare, Terminal } from 'lucide-react';

interface DemoGuideProps {
  currentStep: number;
  onSelectStep: (step: number) => void;
  onExecuteFullRun: () => void;
  onTriggerClaimFail: () => void;
  onResolveClaim: () => void;
  onTriggerEmotionFail: () => void;
  onReworkScene: () => void;
  onOpenLiveMode: () => void;
  onOpenEvolution: () => void;
}

export const DemoGuide: React.FC<DemoGuideProps> = ({
  currentStep,
  onSelectStep,
  onExecuteFullRun,
  onTriggerClaimFail,
  onResolveClaim,
  onTriggerEmotionFail,
  onReworkScene,
  onOpenLiveMode,
  onOpenEvolution
}) => {
  // Starts minimized. The guide is a floating overlay, so opening it by default
  // covered the evidence panels it is meant to point at.
  const [minimized, setMinimized] = useState(true);

  const steps = [
    {
      num: 1,
      title: "Inspect / Compile Maya",
      desc: "Digital DNA v1.7.0 with ArcFace face & voice lock and Ed25519 rights binding.",
      action: () => onSelectStep(1),
      btnText: "Inspect Maya v1.7"
    },
    {
      num: 2,
      title: "Give One Command",
      desc: "'Create a 60s product launch for Indian developers. Research docs. English & Hindi.'",
      action: onExecuteFullRun,
      btnText: "Execute Campaign DAG"
    },
    {
      num: 3,
      title: "Observe Agent Activity",
      desc: "Supervised DAG: Research (18 docs), Critic (adversarial revision), Director emotional arc.",
      action: () => onSelectStep(3),
      btnText: "View Agent DAG"
    },
    {
      num: 4,
      title: "Trigger Claim Block (Step 4)",
      desc: "Deliberate claim '3x faster' blocked by Guardian -> Attach benchmark PDF -> Approved!",
      action: onTriggerClaimFail,
      btnText: "Trigger Unsupported Claim"
    },
    {
      num: 5,
      title: "Trigger Emotion Fail (Step 5)",
      desc: "Scene 4 emotion mismatch -> Guardian flags REWORK -> Regenerates Scene 4 only!",
      action: onTriggerEmotionFail,
      btnText: "Trigger Emotion Mismatch"
    },
    {
      num: 6,
      title: "Inspect Multi-Asset Output",
      desc: "Master EN video, Hindi culturally-adapted re-performance, 3 vertical 9:16 Shorts.",
      action: () => onSelectStep(6),
      btnText: "View Assets & C2PA"
    },
    {
      num: 7,
      title: "Test Live Mode",
      desc: "Talk to Maya in real-time (<800ms). Switch register: Beginner vs CTO while DNA is locked.",
      action: onOpenLiveMode,
      btnText: "Open Live Mode"
    },
    {
      num: 8,
      title: "ClickHouse Telemetry",
      desc: "Analyze 1,842 scene impressions across platforms, statistical CI validation.",
      action: onOpenEvolution,
      btnText: "Open ClickHouse Loop"
    },
    {
      num: 9,
      title: "Prove Loop Closed (Plan Diff)",
      desc: "Director Plan visibly diffs between Run #1 and Run #2, citing ClickHouse query.",
      action: onOpenEvolution,
      btnText: "View Step 9 Plan Diff"
    }
  ];

  if (minimized) {
    return (
      <button
        onClick={() => setMinimized(false)}
        className="btn btn-primary"
        style={{
          position: 'fixed',
          bottom: '150px',
          right: '24px',
          zIndex: 99,
          boxShadow: '0 8px 30px rgba(0,0,0,0.7)',
          padding: '8px 16px',
          fontSize: '12px'
        }}
      >
        <Sparkles size={14} />
        Open 9-Step Demo Guide
      </button>
    );
  }

  return (
    <div
      className="glass-panel"
      style={{
        position: 'fixed',
        bottom: '150px',
        right: '24px',
        width: '360px',
        zIndex: 99,
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.8), 0 0 20px rgba(99,102,241,0.25)',
        border: '1px solid var(--border-focus)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="var(--primary-light)" />
          <span style={{ fontWeight: 800, fontSize: '13px', letterSpacing: '0.5px' }}>
            THE WINNING DEMO (9 STEPS)
          </span>
        </div>
        <button
          onClick={() => setMinimized(true)}
          style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '12px' }}
        >
          ✕
        </button>
      </div>

      <div style={{ maxHeight: '280px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {steps.map((s) => {
          const isCurrent = s.num === currentStep;
          return (
            <div
              key={s.num}
              onClick={() => onSelectStep(s.num)}
              style={{
                padding: '8px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isCurrent ? 'var(--bg-surface-elevated)' : 'rgba(0,0,0,0.3)',
                border: isCurrent ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700, fontSize: '11px', color: isCurrent ? 'var(--primary-light)' : 'var(--text-primary)' }}>
                  Step {s.num}: {s.title}
                </span>
                <ChevronRight size={12} color="var(--text-muted)" />
              </div>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px', lineHeight: 1.3 }}>
                {s.desc}
              </p>
              {isCurrent && (
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', marginTop: '6px', padding: '4px 8px', fontSize: '10px' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    s.action();
                  }}
                >
                  {s.btnText}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
