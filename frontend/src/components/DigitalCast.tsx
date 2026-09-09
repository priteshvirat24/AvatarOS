import React from 'react';
import { ShieldCheck, Sparkles, Sliders, Dna, FileCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface CastMember {
  character_id: string;
  name: string;
  version: string;
  status: string;
  voice_model: string;
  accent: string;
  identity_confidence: number;
  rights_status: string;
  primary_topics: string[];
}

interface DigitalCastProps {
  cast: CastMember[];
  selectedId: string;
  onSelect: (id: string) => void;
  onOpenCompiler: () => void;
  onOpenDnaModal: (characterId: string) => void;
}

export const DigitalCast: React.FC<DigitalCastProps> = ({
  cast,
  selectedId,
  onSelect,
  onOpenCompiler,
  onOpenDnaModal,
}) => {
  return (
    <aside style={{
      width: '280px',
      borderRight: '1px solid var(--border-subtle)',
      backgroundColor: 'var(--color-surface)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      flexShrink: 0
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700, letterSpacing: '0.5px', color: 'var(--text-secondary)' }}>
              DIGITAL CAST
            </span>
            <span className="badge-neon badge-primary" style={{ padding: '2px 8px', fontSize: '10px' }}>
              {cast.length} ACTORS
            </span>
          </div>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            Persistent Identities &amp; DNA
          </p>
        </div>
        <button
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '11px' }}
          onClick={onOpenCompiler}
          title="Compile New Character"
        >
          <Sparkles size={13} color="var(--color-primary)" />
          Compile
        </button>
      </div>

      {/* Cast List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
        {cast.map((c) => {
          const isSelected = c.character_id === selectedId;
          const avatarGradients: Record<string, string> = {
            maya: 'linear-gradient(135deg, #4285F4 0%, #1A73E8 100%)', // Google Blue
            aria: 'linear-gradient(135deg, #EA4335 0%, #C5221F 100%)', // Google Red
            david: 'linear-gradient(135deg, #FBBC04 0%, #EA8600 100%)', // Google Yellow
            nova: 'linear-gradient(135deg, #34A853 0%, #137333 100%)', // Google Green
          };

          return (
            <motion.div
              key={c.character_id}
              onClick={() => onSelect(c.character_id)}
              whileHover={{ x: 2 }}
              whileTap={{ scale: 0.99 }}
              style={{
                backgroundColor: isSelected ? 'var(--color-surface-elevated)' : 'transparent',
                border: isSelected ? '1px solid var(--color-primary)' : '1px solid transparent',
                borderRadius: 'var(--radius-md)',
                padding: '12px',
                marginBottom: '8px',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease',
                position: 'relative',
              }}
            >
              {isSelected && (
                <div style={{
                  position: 'absolute',
                  left: 0,
                  top: '15%',
                  bottom: '15%',
                  width: '3px',
                  backgroundColor: 'var(--color-primary)',
                  borderRadius: '0 2px 2px 0'
                }} />
              )}

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {/* Avatar Initials Circle */}
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: avatarGradients[c.character_id] || avatarGradients.maya,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 800,
                  fontSize: '15px',
                  boxShadow: isSelected ? '0 0 12px rgba(66, 133, 244, 0.4)' : 'none',
                  flexShrink: 0
                }}>
                  {c.name[0]}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                      {c.name}
                    </span>
                    <span className="badge-neon badge-cyan" style={{ fontSize: '10px', padding: '1px 6px' }}>
                      {c.version}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
                    <div className="status-dot active" />
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      {c.accent.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              {/* Sparkline & Rights Info */}
              <div style={{
                marginTop: '10px',
                paddingTop: '8px',
                borderTop: '1px solid rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '11px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-emerald)' }}>
                  <ShieldCheck size={12} />
                  <span>ArcFace: {(c.identity_confidence * 100).toFixed(0)}%</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenDnaModal(c.character_id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--primary-light)',
                    cursor: 'pointer',
                    fontSize: '11px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px'
                  }}
                  title="View Digital DNA"
                >
                  <Dna size={11} />
                  DNA
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Rights Governance Footer */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-darkest)',
        fontSize: '11px',
        color: 'var(--text-muted)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
          <FileCheck size={13} color="var(--accent-emerald)" />
          <span style={{ fontWeight: 600 }}>C2PA Vault Enforced</span>
        </div>
        <p style={{ marginTop: '2px', fontSize: '10px' }}>
          All productions bound to Ed25519 signed rights agreements.
        </p>
      </div>
    </aside>
  );
};
