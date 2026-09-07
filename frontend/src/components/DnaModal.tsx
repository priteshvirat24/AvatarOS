import React, { useState, useEffect } from 'react';
import { X, Dna, GitCompare, CheckCircle2, ShieldCheck, FileText } from 'lucide-react';

interface DnaModalProps {
  characterId: string;
  onClose: () => void;
}

export const DnaModal: React.FC<DnaModalProps> = ({ characterId, onClose }) => {
  const [dna, setDna] = useState<any>(null);
  const [diff, setDiff] = useState<any>(null);
  const [viewTab, setViewTab] = useState<'dna' | 'diff'>('dna');

  useEffect(() => {
    fetch(`/api/cast/${characterId}/dna`)
      .then((r) => r.json())
      .then((d) => setDna(d))
      .catch(console.error);

    if (characterId === 'maya') {
      fetch('/api/cast/maya/diff')
        .then((r) => r.json())
        .then((d) => setDiff(d))
        .catch(console.error);
    }
  }, [characterId]);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '24px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '820px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        border: '1px solid var(--border-focus)'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-base)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Dna size={20} color="var(--primary-light)" />
            <div>
              <h3 style={{ fontSize: '15px', fontWeight: 700 }}>
                DIGITAL DNA SPECIFICATION — {characterId.toUpperCase()} {dna?.version}
              </h3>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Canonical Schema Contract (Section 4.1) &bull; Checksum: {dna?.checksum?.slice(0, 24)}...
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {characterId === 'maya' && (
              <div style={{ display: 'flex', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', padding: '2px' }}>
                <button
                  onClick={() => setViewTab('dna')}
                  style={{
                    padding: '4px 8px',
                    fontSize: '11px',
                    background: viewTab === 'dna' ? 'var(--primary)' : 'transparent',
                    color: viewTab === 'dna' ? 'white' : 'var(--text-muted)',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Current DNA
                </button>
                <button
                  onClick={() => setViewTab('diff')}
                  style={{
                    padding: '4px 8px',
                    fontSize: '11px',
                    background: viewTab === 'diff' ? 'var(--primary)' : 'transparent',
                    color: viewTab === 'diff' ? 'white' : 'var(--text-muted)',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  <GitCompare size={11} style={{ marginRight: '3px', verticalAlign: 'middle' }} />
                  Diff (v1.0 → v1.7)
                </button>
              </div>
            )}
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
          {viewTab === 'dna' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Personality Vector Cards */}
              <div>
                <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)' }}>
                  PERSONALITY VECTOR (6 TRAIT DIMENSIONS)
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginTop: '8px' }}>
                  {dna?.personality_vector && Object.entries(dna.personality_vector).map(([k, v]: [string, any]) => (
                    <div key={k} style={{
                      backgroundColor: 'var(--bg-darkest)',
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-subtle)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                        <span style={{ textTransform: 'capitalize' }}>{k}</span>
                        <strong style={{ color: 'var(--primary-light)' }}>{(v * 100).toFixed(0)}%</strong>
                      </div>
                      <div style={{ height: '4px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '6px', overflow: 'hidden' }}>
                        <div style={{ width: `${v * 100}%`, height: '100%', backgroundColor: 'var(--primary)' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Topics Boundaries */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                    ALLOWED TOPICS (APPROVED GROUNDING)
                  </span>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                    {dna?.topics?.allowed?.map((t: string) => (
                      <span key={t} className="badge-neon badge-emerald" style={{ fontSize: '10px' }}>
                        {t.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ backgroundColor: 'var(--bg-darkest)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--accent-rose)' }}>
                    RESTRICTED TOPICS (HARD WRITE-GUARDED)
                  </span>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                    {dna?.topics?.restricted?.map((t: string) => (
                      <span key={t} className="badge-neon badge-rose" style={{ fontSize: '10px' }}>
                        {t.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Raw JSON Schema Viewer */}
              <div>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)' }}>
                  CANONICAL MACHINE CONTRACT (JSON)
                </span>
                <pre style={{
                  backgroundColor: 'var(--bg-darkest)',
                  padding: '12px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--accent-cyan)',
                  marginTop: '6px',
                  overflowX: 'auto'
                }}>
                  {JSON.stringify(dna, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            /* Diff Viewer (Section 3.2) */
            <div>
              <div style={{ marginBottom: '14px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Semantic Version Diff: Maya v1.0.0 → v1.7.0</h4>
                <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Structured audit trail tracking evolutionary optimizations and allowed topic extensions.
                </p>
              </div>

              <pre style={{
                backgroundColor: 'var(--bg-darkest)',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-primary)',
                lineHeight: 1.6
              }}>
                <span style={{ color: 'var(--text-muted)' }}>diff MAYA v1.0.0 → v1.7.0</span>{'\n'}
                <span style={{ color: 'var(--text-muted)' }}>────────────────────────────────────────</span>{'\n'}
                <span style={{ color: 'var(--accent-emerald)' }}>+ ALLOWED_TOPICS: "developer_tooling"</span>{'\n'}
                <span style={{ color: 'var(--accent-cyan)' }}>~ SPEECH.pace_multiplier: 1.00x → 1.02x (Evolution Agent, confidence 0.83)</span>{'\n'}
                <span style={{ color: 'var(--accent-cyan)' }}>~ GESTURE_PROFILE.expressiveness: 0.62 → 0.78</span>{'\n'}
                <span style={{ color: 'var(--accent-cyan)' }}>~ PERSONALITY.witty: 0.50 → 0.64</span>{'\n'}
                <span style={{ color: 'var(--text-dim)' }}>  (unchanged: VISUAL_IDENTITY ArcFace lock, VOICE model, RESTRICTED_TOPICS, RIGHTS)</span>
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
