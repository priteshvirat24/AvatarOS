import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, CheckCircle2, AlertCircle, Cloud, Server, Database, Sparkles, Cpu, Layers } from 'lucide-react';

interface ProviderMatrixModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ProviderMatrixModal: React.FC<ProviderMatrixModalProps> = ({ isOpen, onClose }) => {
  const [matrixData, setMatrixData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch('/api/production/provider-matrix')
        .then((r) => r.json())
        .then((data) => {
          setMatrixData(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to load provider matrix:", err);
          setLoading(false);
        });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const matrix = matrixData?.matrix || {};
  const env = matrixData?.environment || 'development';
  const version = matrixData?.version || '1.0.0';

  const rows = [
    { key: 'ai', name: 'AI Reasoning', icon: Sparkles, data: matrix.ai },
    { key: 'knowledge_embeddings', name: 'Knowledge & Vector Search', icon: Layers, data: matrix.knowledge_embeddings },
    { key: 'voice', name: 'Voice Synthesis', icon: Cpu, data: matrix.voice },
    { key: 'avatar_renderer', name: 'Avatar & Media Renderer', icon: Server, data: matrix.avatar_renderer },
    { key: 'guardian', name: 'Multimodal Guardian', icon: ShieldCheck, data: matrix.guardian },
    { key: 'asr', name: 'ASR / Speech Recognition', icon: Cpu, data: matrix.asr },
    { key: 'live', name: 'Live Conversation (Gemini Live)', icon: Sparkles, data: matrix.live },
    { key: 'mistral', name: 'Mistral Conversational Fallback', icon: Cpu, data: matrix.mistral },
    { key: 'clickhouse', name: 'ClickHouse Analytics', icon: Database, data: matrix.clickhouse },
    { key: 'mcp', name: 'MCP Partner Gateway', icon: Server, data: matrix.mcp },
    { key: 'storage', name: 'Media Storage', icon: Cloud, data: matrix.storage }
  ];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(5, 8, 15, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div style={{
        width: '880px',
        maxHeight: '90vh',
        backgroundColor: 'var(--bg-base)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-darkest)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--primary-light)'
            }}>
              <Cloud size={18} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h2 style={{ fontSize: '16px', fontWeight: 800 }}>Production Provider Matrix &amp; Cloud Readiness</h2>
                <span className="badge-neon badge-primary" style={{ fontSize: '10px' }}>v{version}</span>
                <span className={`badge-neon ${env === 'production' ? 'badge-success' : 'badge-amber'}`} style={{ fontSize: '10px' }}>
                  {env.toUpperCase()}
                </span>
              </div>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Honest observability contract: Real cloud API integrations vs deterministic offline test engines.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{ padding: '6px', borderRadius: '50%' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Modal Content */}
        <div style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              Loading provider status...
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px' }}>
                  <th style={{ padding: '10px 8px' }}>Subsystem</th>
                  <th style={{ padding: '10px 8px' }}>Real Cloud Provider</th>
                  <th style={{ padding: '10px 8px' }}>Deterministic Fallback</th>
                  <th style={{ padding: '10px 8px' }}>Active Engine</th>
                  <th style={{ padding: '10px 8px', textAlign: 'center' }}>Runtime Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => {
                  const Icon = row.icon;
                  const item = row.data || {};
                  const isReal = item.is_real;

                  return (
                    <tr key={row.key} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '12px 8px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Icon size={14} color="var(--primary-light)" />
                        {row.name}
                      </td>
                      <td style={{ padding: '12px 8px', color: 'var(--text-secondary)' }}>
                        <code>{item.real_provider || 'N/A'}</code>
                      </td>
                      <td style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>
                        <code>{item.deterministic_fallback || 'N/A'}</code>
                      </td>
                      <td style={{ padding: '12px 8px', color: isReal ? '#38BDF8' : '#F59E0B', fontWeight: 500 }}>
                        <code>{item.active || 'active'}</code>
                      </td>
                      <td style={{ padding: '12px 8px', textAlign: 'center' }}>
                        {isReal ? (
                          <span style={{
                            padding: '3px 8px',
                            borderRadius: '4px',
                            backgroundColor: 'rgba(16, 185, 129, 0.15)',
                            color: '#10B981',
                            fontSize: '10px',
                            fontWeight: 700,
                            border: '1px solid rgba(16, 185, 129, 0.3)'
                          }}>
                            REAL API
                          </span>
                        ) : (
                          <span style={{
                            padding: '3px 8px',
                            borderRadius: '4px',
                            backgroundColor: 'rgba(245, 158, 11, 0.12)',
                            color: '#F59E0B',
                            fontSize: '10px',
                            fontWeight: 700,
                            border: '1px solid rgba(245, 158, 11, 0.25)'
                          }}>
                            DETERMINISTIC
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          {/* Safety & Compliance Invariant Box */}
          <div style={{
            marginTop: '20px',
            padding: '14px',
            backgroundColor: 'rgba(99, 102, 241, 0.05)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            borderRadius: 'var(--radius-md)',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            lineHeight: '1.6'
          }}>
            <strong style={{ color: 'var(--primary-light)' }}>Google Cloud &amp; Safety Invariant:</strong> In development / offline testing, all subsystems run with reproducible deterministic engines ensuring 100% test passing without live credentials. When deployed to Google Cloud Run with Secret Manager keys, the system seamlessly transitions to live Gemini 2.5, Gemini Live, Cloud TTS, and ClickHouse while preserving immutable Digital DNA and Publication Gate constraints.
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '12px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'flex-end',
          backgroundColor: 'var(--bg-darkest)'
        }}>
          <button className="btn btn-secondary" onClick={onClose} style={{ fontSize: '12px' }}>
            Close Matrix
          </button>
        </div>
      </div>
    </div>
  );
};
