import React from 'react';

interface ProductionTimelineProps {
  shots: any[];
  activeSceneNo: number;
  onSelectScene: (sceneNo: number) => void;
  failedScenes?: number[];
  isBlocked?: boolean;
}

export const ProductionTimeline: React.FC<ProductionTimelineProps> = ({
  shots = [],
  activeSceneNo,
  onSelectScene,
  failedScenes = [],
  isBlocked = false
}) => {
  const defaultScenes = [
    { scene_no: 1, role: "Hook", duration_s: 6.8, target_emotion: "curious", emotional_intensity: 0.55, shot: "close_up" },
    { scene_no: 2, role: "Problem", duration_s: 12.0, target_emotion: "concerned", emotional_intensity: 0.35, shot: "medium_shot" },
    { scene_no: 3, role: "Product", duration_s: 14.0, target_emotion: "confident", emotional_intensity: 0.60, shot: "medium_close_up" },
    { scene_no: 4, role: "Demonstration", duration_s: 15.0, target_emotion: "excited", emotional_intensity: 0.78, shot: "medium_close_up" },
    { scene_no: 5, role: "CTA", duration_s: 10.0, target_emotion: "direct", emotional_intensity: 0.70, shot: "medium_shot" }
  ];

  const displayShots = shots.length ? shots : defaultScenes;
  const totalDuration = displayShots.reduce((acc, s) => acc + (s.duration_s || 10), 0);

  return (
    <footer style={{
      height: '140px',
      borderTop: '1px solid var(--border-subtle)',
      backgroundColor: 'var(--bg-base)',
      display: 'flex',
      flexDirection: 'column',
      padding: '12px 20px',
      flexShrink: 0
    }}>
      {/* Header bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '1px', color: 'var(--text-secondary)' }}>
            PRODUCTION TIMELINE
          </span>
          <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>
            5 SCENES | {totalDuration.toFixed(1)}s TARGET
          </span>
        </div>

        {/* Emotion curve key */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: 'var(--accent-emerald)' }} />
            <span>Guardian Approved</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: 'var(--accent-amber)' }} />
            <span>Scene-Scoped Rework</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '2px', backgroundColor: 'var(--accent-rose)' }} />
            <span>Blocked / Rework</span>
          </div>
        </div>
      </div>

      {/* Track Blocks */}
      <div style={{
        flex: 1,
        display: 'flex',
        gap: '6px',
        position: 'relative',
        backgroundColor: 'var(--bg-darkest)',
        padding: '6px',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)'
      }}>
        {displayShots.map((shot: any) => {
          const isSelected = shot.scene_no === activeSceneNo;
          const isFailed = failedScenes.includes(shot.scene_no);
          const flexRatio = (shot.duration_s || 10) / totalDuration;

          let statusColor = 'var(--accent-emerald)';
          let statusLabel = 'APPROVED';
          if (isBlocked && shot.scene_no === 4) {
            statusColor = 'var(--accent-rose)';
            statusLabel = 'CLAIM BLOCKED';
          } else if (isFailed) {
            statusColor = 'var(--accent-amber)';
            statusLabel = 'EMOTION MISMATCH';
          }

          return (
            <div
              key={shot.scene_no}
              onClick={() => onSelectScene(shot.scene_no)}
              style={{
                flex: flexRatio,
                backgroundColor: isSelected ? 'var(--bg-surface-elevated)' : 'var(--bg-surface)',
                border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                cursor: 'pointer',
                position: 'relative',
                transition: 'all 0.2s ease',
                overflow: 'hidden'
              }}
              onMouseEnter={(e) => {
                if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-focus)';
              }}
              onMouseLeave={(e) => {
                if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-subtle)';
              }}
            >
              {/* Emotional Intensity bar indicator */}
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '3px',
                backgroundColor: statusColor
              }} />

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-primary)' }}>
                  SCENE 0{shot.scene_no}
                </span>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {shot.duration_s}s
                </span>
              </div>

              <div>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary-light)' }}>
                  {shot.role?.toUpperCase()}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '2px' }}>
                  <span style={{ fontSize: '10px', color: 'var(--accent-amber)', fontFamily: 'var(--font-mono)' }}>
                    {shot.target_emotion} ({(shot.emotional_intensity * 100).toFixed(0)}%)
                  </span>
                  <span style={{ fontSize: '9px', color: statusColor, fontWeight: 700 }}>
                    {statusLabel}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </footer>
  );
};
