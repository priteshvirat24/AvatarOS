import React, { useCallback, useEffect, useState } from 'react';
import {
  AlertTriangle, CheckCircle2, Database, Loader2, RefreshCw, ShieldAlert, ShieldCheck
} from 'lucide-react';

/**
 * Governance forensics.
 *
 * Every gate, rights and Guardian decision is appended to an immutable ClickHouse
 * table as it happens. This panel reads them back through the official
 * mcp-clickhouse server, which turns "why was this promo blocked?" into a query
 * with a reason code and a trace id instead of a hunt through log files.
 */

interface GovernanceEvent {
  event_id: string;
  ts: string;
  trace_id: string;
  run_id: string;
  character_id: string;
  character_version: string;
  stage: string;
  decision: string;
  reason_code: string;
  severity: string;
  detail: string;
}

interface SummaryRow {
  stage: string;
  decision: string;
  n: number;
}

type Filter = 'ALL' | 'BLOCK' | 'WARN' | 'PASS';

const decisionBadge = (decision: string) => {
  switch (decision) {
    case 'BLOCK':
      return { cls: 'badge-rose', icon: <ShieldAlert size={11} /> };
    case 'WARN':
      return { cls: 'badge-amber', icon: <AlertTriangle size={11} /> };
    default:
      return { cls: 'badge-emerald', icon: <ShieldCheck size={11} /> };
  }
};

const formatTime = (ts: string) => {
  if (!ts) return '--';
  const parsed = new Date(ts.includes('T') ? ts : ts.replace(' ', 'T') + 'Z');
  if (Number.isNaN(parsed.getTime())) return ts;
  return parsed.toISOString().replace('T', ' ').slice(0, 19);
};

export const GovernanceLedger: React.FC = () => {
  const [events, setEvents] = useState<GovernanceEvent[]>([]);
  const [summary, setSummary] = useState<SummaryRow[]>([]);
  const [sql, setSql] = useState<string>('');
  const [serverIdentity, setServerIdentity] = useState<string>('');
  const [latency, setLatency] = useState<number | null>(null);
  const [simulated, setSimulated] = useState(false);
  const [filter, setFilter] = useState<Filter>('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSql, setShowSql] = useState(false);

  const load = useCallback(async (nextFilter: Filter) => {
    setLoading(true);
    setError(null);
    try {
      const query = nextFilter === 'ALL' ? '' : `&decision=${nextFilter}`;
      const [ledgerRes, summaryRes] = await Promise.all([
        fetch(`/api/governance/ledger?limit=60${query}`),
        fetch('/api/governance/summary'),
      ]);

      if (!ledgerRes.ok) {
        const body = await ledgerRes.json().catch(() => ({}));
        throw new Error(body.detail || `Ledger unavailable (HTTP ${ledgerRes.status})`);
      }

      const ledger = await ledgerRes.json();
      setEvents(ledger.events || []);
      setSql(ledger.compiled_sql || '');
      setServerIdentity(ledger.server_identity || '');
      setLatency(ledger.latency_ms ?? null);
      setSimulated(Boolean(ledger.is_simulated));

      if (summaryRes.ok) {
        const s = await summaryRes.json();
        setSummary(s.breakdown || []);
      } else {
        setSummary([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to read the governance ledger');
      setEvents([]);
      setSummary([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(filter); }, [filter, load]);

  const blocked = summary.filter((r) => r.decision === 'BLOCK').reduce((a, r) => a + r.n, 0);
  const warned = summary.filter((r) => r.decision === 'WARN').reduce((a, r) => a + r.n, 0);
  const passed = summary.filter((r) => r.decision === 'PASS').reduce((a, r) => a + r.n, 0);
  const total = blocked + warned + passed;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', height: '100%' }}>

      {/* Header */}
      <div className="glass-panel" style={{ padding: '14px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldCheck size={17} color="var(--accent-emerald)" />
            <div>
              <span style={{ fontSize: '13px', fontWeight: 800, letterSpacing: '0.3px' }}>
                GOVERNANCE FORENSICS
              </span>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Immutable decision ledger — every block is a row with a reason code, queried from ClickHouse
                {serverIdentity ? ` via ${serverIdentity}` : ''}
                {latency !== null ? ` · ${latency}ms` : ''}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {sql && (
              <button
                className="btn btn-secondary"
                onClick={() => setShowSql((v) => !v)}
                style={{ padding: '5px 10px', fontSize: '10px' }}
              >
                <Database size={12} /> {showSql ? 'Hide SQL' : 'Show SQL'}
              </button>
            )}
            <button
              className="btn btn-secondary"
              onClick={() => load(filter)}
              disabled={loading}
              style={{ padding: '5px 10px', fontSize: '10px' }}
            >
              {loading ? <Loader2 size={12} className="animate-spin" /> : <RefreshCw size={12} />}
              Refresh
            </button>
          </div>
        </div>

        {simulated && (
          <div
            style={{
              marginTop: '10px', padding: '8px 10px', borderRadius: 'var(--radius-sm)',
              backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)',
              fontSize: '10px', color: 'var(--accent-amber)'
            }}
          >
            Deterministic fallback mode — no ClickHouse cluster is configured, so there is no governance ledger to
            read. Figures are not shown rather than simulated.
          </div>
        )}

        {showSql && sql && (
          <pre
            className="code-font"
            style={{
              marginTop: '10px', fontSize: '9.5px', color: 'var(--text-secondary)',
              backgroundColor: 'var(--bg-darkest)', padding: '10px',
              borderRadius: 'var(--radius-sm)', overflowX: 'auto', maxHeight: '160px'
            }}
          >
            {sql}
          </pre>
        )}
      </div>

      {/* Decision tiles */}
      {total > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '10px' }}>
          {[
            { label: 'Decisions recorded', value: total, color: 'var(--text-primary)' },
            { label: 'Passed', value: passed, color: 'var(--accent-emerald)' },
            { label: 'Blocked', value: blocked, color: 'var(--accent-rose)' },
            { label: 'Reworked / warned', value: warned, color: 'var(--accent-amber)' },
          ].map((tile) => (
            <div key={tile.label} className="glass-panel" style={{ padding: '12px 14px' }}>
              <div style={{ fontSize: '22px', fontWeight: 800, color: tile.color, lineHeight: 1.1 }}>
                {tile.value}
              </div>
              <div style={{ fontSize: '9.5px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.6px', marginTop: '3px' }}>
                {tile.label}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '6px' }}>
        {(['ALL', 'BLOCK', 'WARN', 'PASS'] as Filter[]).map((f) => (
          <button
            key={f}
            className="btn"
            onClick={() => setFilter(f)}
            style={{
              padding: '5px 12px', fontSize: '10px',
              backgroundColor: filter === f ? 'var(--primary)' : 'var(--bg-surface)',
              color: filter === f ? 'white' : 'var(--text-muted)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            {f === 'ALL' ? 'All decisions' : f}
          </button>
        ))}
      </div>

      {/* Events */}
      <div className="glass-panel" style={{ flex: 1, overflowY: 'auto', minHeight: 0, padding: '4px' }}>
        {error ? (
          <div style={{ padding: '30px 20px', textAlign: 'center' }}>
            <AlertTriangle size={24} color="var(--accent-rose)" />
            <p style={{ fontSize: '12px', color: 'var(--accent-rose)', marginTop: '10px', fontWeight: 600 }}>{error}</p>
            <button className="btn btn-secondary" onClick={() => load(filter)} style={{ marginTop: '12px', fontSize: '10px' }}>
              <RefreshCw size={12} /> Try again
            </button>
          </div>
        ) : loading ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Loader2 size={22} className="animate-spin" />
            <p style={{ fontSize: '11px', marginTop: '10px' }}>Querying the governance ledger…</p>
          </div>
        ) : events.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center' }}>
            <Database size={26} color="var(--text-dim)" />
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '10px', fontWeight: 600 }}>
              No {filter === 'ALL' ? '' : `${filter} `}decisions recorded yet
            </p>
            <p style={{ fontSize: '10.5px', color: 'var(--text-muted)', marginTop: '6px', maxWidth: '400px', marginLeft: 'auto', marginRight: 'auto', lineHeight: 1.6 }}>
              Run a production from Studio Mode — every stage decision it makes is appended here.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {events.map((e) => {
              const badge = decisionBadge(e.decision);
              return (
                <div
                  key={e.event_id}
                  style={{
                    padding: '10px 12px',
                    borderBottom: '1px solid var(--border-subtle)',
                    display: 'flex', gap: '12px', alignItems: 'flex-start'
                  }}
                >
                  <span className={`badge-neon ${badge.cls}`} style={{ fontSize: '8.5px', flexShrink: 0, marginTop: '2px' }}>
                    {badge.icon} {e.decision}
                  </span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                        {e.stage.replace(/_/g, ' ')}
                      </span>
                      {e.reason_code && (
                        <span className="code-font" style={{ fontSize: '9px', color: 'var(--accent-rose)' }}>
                          {e.reason_code}
                        </span>
                      )}
                    </div>
                    <p style={{ fontSize: '10.5px', color: 'var(--text-secondary)', marginTop: '3px', lineHeight: 1.5 }}>
                      {e.detail || '—'}
                    </p>
                    <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginTop: '5px', fontSize: '9px', color: 'var(--text-muted)' }}>
                      <span className="code-font">{formatTime(e.ts)}</span>
                      <span>trace: <span className="code-font">{e.trace_id}</span></span>
                      {e.run_id && <span>run: <span className="code-font">{e.run_id}</span></span>}
                      <span>{e.character_id}{e.character_version ? ` ${e.character_version}` : ''}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
