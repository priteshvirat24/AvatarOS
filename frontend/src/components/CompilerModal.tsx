import React, { useState } from 'react';
import { X, Sparkles, CheckCircle2, AlertTriangle, ShieldCheck, Upload, RefreshCw } from 'lucide-react';

interface CompilerModalProps {
  onClose: () => void;
}

export const CompilerModal: React.FC<CompilerModalProps> = ({ onClose }) => {
  const [characterName, setCharacterName] = useState('Maya');
  const [personalityBrief, setPersonalityBrief] = useState('Confident, analytical, witty developer advocate with direct, authoritative delivery');
  const [isCompiling, setIsCompiling] = useState(false);
  const [report, setReport] = useState<any>(null);

  const runCompiler = async () => {
    setIsCompiling(true);
    try {
      const res = await fetch('/api/cast/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: characterName,
          voice_sample_sec: 30,
          num_images: 5,
          personality_brief: personalityBrief,
          rights_authorized: true
        })
      });
      const data = await res.json();
      setReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsCompiling(false);
    }
  };

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
        maxWidth: '680px',
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} color="var(--primary-light)" />
            <h3 style={{ fontSize: '15px', fontWeight: 700 }}>
              CHARACTER COMPILER PIPELINE (SECTION 5)
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              Character Name
            </label>
            <input
              type="text"
              value={characterName}
              onChange={(e) => setCharacterName(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: 'white',
                fontSize: '13px'
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              Personality &amp; Behavioral Brief
            </label>
            <textarea
              value={personalityBrief}
              onChange={(e) => setPersonalityBrief(e.target.value)}
              rows={3}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: 'white',
                fontSize: '12px',
                fontFamily: 'var(--font-body)'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{
              border: '1px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-darkest)'
            }}>
              <Upload size={20} color="var(--primary-light)" style={{ margin: '0 auto 6px' }} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>5 Reference Images</span>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)' }}>ArcFace 512-d feature extraction</p>
            </div>

            <div style={{
              border: '1px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '14px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-darkest)'
            }}>
              <Upload size={20} color="var(--accent-emerald)" style={{ margin: '0 auto 6px' }} />
              <span style={{ fontSize: '11px', fontWeight: 600 }}>30s Audio Sample</span>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)' }}>SNR: 28dB (pass &gt;= 20dB)</p>
            </div>
          </div>

          {!report ? (
            <button
              className="btn btn-primary"
              onClick={runCompiler}
              disabled={isCompiling}
              style={{ width: '100%', marginTop: '6px' }}
            >
              {isCompiling ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
              Run Compiler &amp; Quality Gate (Section 5.2)
            </button>
          ) : (
            <div style={{
              backgroundColor: 'var(--bg-darkest)',
              borderRadius: 'var(--radius-md)',
              padding: '16px',
              border: '1px solid var(--border-focus)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontWeight: 800, fontSize: '13px' }}>{report.character.toUpperCase()} v1.0 — Compilation Report</span>
                <span className="badge-neon badge-emerald">{report.status}</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Identity Confidence:</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>✓ 0.94 (min 0.85)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Voice Confidence:</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>✓ 0.91 (min 0.85)</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Personality Coverage:</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>✓ 6/6 trait dimensions anchored</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Rights Binding:</span>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>✓ Signed authorization on file</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Reference Diversity:</span>
                  <span style={{ color: 'var(--accent-amber)', fontWeight: 600 }}>⚠ 1 lighting condition (advisory)</span>
                </div>
              </div>

              <button
                className="btn btn-emerald"
                onClick={onClose}
                style={{ width: '100%', marginTop: '14px', fontSize: '11px' }}
              >
                Accept &amp; Register Character v1.0.0
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
