import React from 'react';
import { ChevronRight, Sparkles } from 'lucide-react';

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
  isOpen?: boolean;
  onClose?: () => void;
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
  onOpenEvolution,
  isOpen = false,
  onClose
}) => {
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
      title: "Trigger Controlled Claim Block",
      desc: "Simulate ungrounded marketing claim -> Forced safety gate trip -> 100% hard interlock.",
      action: onTriggerClaimFail,
      btnText: "Trigger Claim Block"
    },
    {
      num: 5,
      title: "Resolve & Re-verify",
      desc: "Inject verified factual citation from ground documentation -> Gate clears to green.",
      action: onResolveClaim,
      btnText: "Resolve Claim & Re-verify"
    },
    {
      num: 6,
      title: "Trigger Guardian Failure",
      desc: "Simulate emotion/energy mismatch in Scene 2 -> Triggers targeted scene-scoped rework.",
      action: onTriggerEmotionFail,
      btnText: "Trigger Emotion Fail"
    },
    {
      num: 7,
      title: "Conversational Live Mode",
      desc: "Sub-800ms full-duplex interactive voice call with Maya using Gemini 2.0 / Mistral stream.",
      action: onOpenLiveMode,
      btnText: "Switch to Live Mode"
    },
    {
      num: 8,
      title: "ClickHouse Real-Time Telemetry",
      desc: "Sub-second event streaming of latency, cost per second, and identity confidence drift.",
      action: onOpenEvolution,
      btnText: "View Telemetry & Evolution"
    },
    {
      num: 9,
      title: "Persona Evolution & A/B Test",
      desc: "Analyze conversion feedback -> Generate new persona generation with mutated traits.",
      action: onOpenEvolution,
      btnText: "Inspect DNA Evolution"
    }
  ];

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: '68px',
        right: '24px',
        width: '360px',
        maxHeight: 'calc(100vh - 100px)',
        zIndex: 9999,
        padding: '16px',
        backgroundColor: 'var(--color-surface-elevated)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '16px',
        boxShadow: '0 12px 36px rgba(0,0,0,0.18), 0 0 0 1px var(--border-focus)',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="var(--google-blue)" />
          <span style={{ fontWeight: 800, fontSize: '13px', letterSpacing: '0.5px', color: 'var(--text-primary)' }}>
            THE WINNING DEMO (9 STEPS)
          </span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              fontSize: '14px',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Close Demo Guide"
          >
            ✕
          </button>
        )}
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
