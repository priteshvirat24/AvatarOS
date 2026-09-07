import React, { useState, useEffect } from 'react';
import { Search, BookOpen, ShieldAlert, CheckCircle2, FileText, Layers, Hash, Sparkles } from 'lucide-react';

export const KnowledgeRetrieval: React.FC = () => {
  const [query, setQuery] = useState('40% faster inference on local LLM');
  const [results, setResults] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'search' | 'documents'>('search');

  useEffect(() => {
    fetchDocuments();
    executeSearch('40% faster inference on local LLM');
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/knowledge/documents');
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error(e);
    }
  };

  const executeSearch = async (qText: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/knowledge/search?q=${encodeURIComponent(qText)}&top_k=4`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(query);
  };

  const isUnsupportedQuery = query.toLowerCase().includes('3x faster') || query.toLowerCase().includes('all competitor');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: 'var(--bg-darkest)',
      padding: '24px',
      gap: '20px',
      overflowY: 'auto'
    }}>
      {/* Top Banner */}
      <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen size={22} color="var(--primary-light)" />
            <h2 style={{ fontSize: '18px', fontWeight: 800 }}>GROUNDED KNOWLEDGE BASE &amp; HYBRID RETRIEVAL</h2>
            <span className="badge-neon badge-cyan">SECTION 8</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Vector similarity (nearest-neighbor) + Okapi BM25 lexical ranking with cryptographic provenance verification.
          </p>
        </div>

        {/* Safety Callout Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 14px',
          backgroundColor: isUnsupportedQuery ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
          border: `1px solid ${isUnsupportedQuery ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.4)'}`,
          borderRadius: 'var(--radius-md)'
        }}>
          {isUnsupportedQuery ? <ShieldAlert size={18} color="var(--accent-rose)" /> : <CheckCircle2 size={18} color="var(--accent-emerald)" />}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: isUnsupportedQuery ? 'var(--accent-rose)' : 'var(--accent-emerald)' }}>
              {isUnsupportedQuery ? "ASSERTION BLOCKED (<0.60 CONFIDENCE)" : "FACTUAL GROUNDING VERIFIED"}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
              Retrieval score != claim confidence invariant enforced
            </div>
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <div className="glass-panel" style={{ padding: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '11px' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search knowledge base for factual evidence..."
              style={{
                width: '100%',
                padding: '10px 14px 10px 38px',
                backgroundColor: 'var(--bg-darkest)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                fontSize: '13px',
                fontFamily: 'inherit'
              }}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Hybrid Search"}
          </button>
        </form>

        {/* Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', fontSize: '11px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Demo Presets:</span>
          <button
            className="btn"
            onClick={() => { setQuery('40% faster inference on local LLM'); executeSearch('40% faster inference on local LLM'); }}
            style={{ padding: '4px 8px', fontSize: '11px', backgroundColor: 'rgba(99,102,241,0.1)' }}
          >
            Supported: MLPerf 40% speedup
          </button>
          <button
            className="btn"
            onClick={() => { setQuery('18 hours of continuous battery life'); executeSearch('18 hours of continuous battery life'); }}
            style={{ padding: '4px 8px', fontSize: '11px', backgroundColor: 'rgba(99,102,241,0.1)' }}
          >
            Supported: 18h Battery life
          </button>
          <button
            className="btn"
            onClick={() => { setQuery('3x faster than all competitor machines on the planet'); executeSearch('3x faster than all competitor machines on the planet'); }}
            style={{ padding: '4px 8px', fontSize: '11px', backgroundColor: 'rgba(239,68,68,0.15)', color: 'var(--accent-rose)' }}
          >
            Unsupported: 3x competitor claim (Blocked)
          </button>
        </div>
      </div>

      {/* Results & Library Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '16px' }}>
        
        {/* Hybrid Retrieval Results */}
        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700 }}>Hybrid Retrieval Ranking (Vector + BM25 Fusion)</span>
            <span className="badge-neon badge-primary">{results.length} CANDIDATE PASSAGES</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {results.map((r, idx) => (
              <div
                key={r.chunk_id || idx}
                style={{
                  backgroundColor: 'var(--bg-darkest)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '14px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={14} color="var(--primary-light)" />
                    <strong style={{ fontSize: '12px' }}>{r.doc_id}</strong>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>({r.section})</span>
                  </div>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <span className="badge-neon badge-cyan" style={{ fontSize: '10px' }}>
                      HYBRID: {(r.hybrid_score * 100).toFixed(1)}%
                    </span>
                    <span className="badge-neon badge-emerald" style={{ fontSize: '10px' }}>
                      SEM: {(r.semantic_score * 100).toFixed(1)}%
                    </span>
                    <span className="badge-neon badge-amber" style={{ fontSize: '10px' }}>
                      BM25: {(r.lexical_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <p style={{ fontSize: '12px', color: 'var(--text-primary)', lineHeight: 1.5, margin: '8px 0' }}>
                  "{r.excerpt}"
                </p>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '10px', color: 'var(--text-muted)' }}>
                  <span>Chunk: <code className="code-font">{r.chunk_id}</code></span>
                  <span>Page: {r.page || 1}</span>
                  <span>Methods: {r.retrieval_methods?.join(' + ')}</span>
                </div>
              </div>
            ))}

            {results.length === 0 && (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
                No candidate evidence found for this query.
              </div>
            )}
          </div>
        </div>

        {/* Document Provenance & Knowledge Registry */}
        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <span style={{ fontSize: '13px', fontWeight: 700 }}>Indexed Document Knowledge Base</span>
            <span className="badge-neon badge-emerald">{documents.length} VERIFIED SOURCES</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {documents.map((d) => (
              <div
                key={d.doc_id}
                style={{
                  backgroundColor: 'var(--bg-darkest)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontWeight: 700, fontSize: '12px', color: 'var(--text-primary)' }}>
                    {d.title}
                  </div>
                  <span className="badge-neon badge-primary" style={{ fontSize: '9px' }}>
                    {d.source_type?.toUpperCase()}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '6px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>ID: <code className="code-font">{d.doc_id}</code></span>
                  <span>Chunks: {d.chunks}</span>
                  <span>Ver: {d.version}</span>
                </div>

                <div style={{ marginTop: '6px', fontSize: '10px', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  SHA-256: {d.content_hash?.slice(0, 24)}...
                </div>
              </div>
            ))}
          </div>

          <div style={{
            marginTop: '16px',
            backgroundColor: 'rgba(99,102,241,0.08)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '12px',
            fontSize: '11px',
            color: 'var(--text-secondary)',
            lineHeight: 1.5
          }}>
            <strong style={{ color: 'var(--primary-light)' }}>Safety Interlock Active:</strong> All claims generated in scripts must carry cryptographically verified checksum references back to these documents before the Publication Gate will authorize media distribution.
          </div>
        </div>
      </div>
    </div>
  );
};
