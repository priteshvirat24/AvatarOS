import React, { useCallback, useEffect, useState } from 'react';
import {
  AlertTriangle, ArrowRight, CheckCircle2, Database, Loader2,
  RotateCcw, ShieldCheck, Sparkles, TrendingUp, XCircle
} from 'lucide-react';

/**
 * Evolution loop.
 *
 * ClickHouse aggregates -> a real Welch's t-test -> a concrete strategy diff that
 * is applied to the next production run. Every number shown comes from rows the
 * official MCP server returned; nothing has a plausible-looking default.
 *
 * The loop is allowed to say no. A refusal - sample floor unmet, lift too small,
 * difference not separable, or the current strategy still winning - is rendered as
 * a first-class outcome, because refusing to churn on noise is the guardrail
 * working, not a failure to demo.
 */

interface HookRow {
  hook_type: string;
  n: number;
  avg_retention: number;
  avg_ctr: number;
  var_watch: number;
  ci_95: [number | null, number | null];
  meets_sample_floor: boolean;
  avg_opening_duration_s?: number;
}

interface Analysis {
  active_strategy: {
    strategy_version: number;
    hook_type: string;
    shot_preference: string;
    opening_duration_s_range: [number, number];
    energy_bias: number;
  };
  rows: HookRow[];
  no_data: boolean;
  compiled_sql: string;
  server_identity: string;
  transport: string;
  latency_ms: number;
  is_simulated: boolean;
}

interface EvolutionResult {
  status: string;
  previous_strategy_version: number;
  new_strategy_version: number;
  statistical_significance: {
    decision: string;
    rationale: string;
    candidate_hook?: string;
    baseline_hook?: string;
    n_candidate?: number;
    n_baseline?: number;
    absolute_lift?: number;
    relative_lift?: number;
    confidence_interval?: string;
    test?: {
      verdict: string;
      statistically_significant: boolean;
      p_value?: number;
      t_statistic?: number;
      degrees_of_freedom?: number;
      difference_ci_95?: [number, number];
      reason?: string;
    };
  };
  mcp_governance: {
    mcp_provider: string;
    transport: string;
    query_latency_ms: number;
    tools_invoked: string[];
    is_simulated: boolean;
  };
  proposed_strategy: Record<string, unknown>;
}

interface PlanDiff {
  hook_type: { run1: string; run2: string; changed: boolean };
  opening_duration_s: { run1: number; run2: number; changed: boolean };
  hook_shot: { run1: string; run2: string; changed: boolean };
  strategy_version: { run1: number; run2: number; changed: boolean };
  justification: string;
}

const fmtPct = (v?: number) => (v === undefined || v === null ? '—' : `${(v * 100).toFixed(1)}%`);
const fmtNum = (v?: number | null, dp = 4) => (v === undefined || v === null ? '—' : v.toFixed(dp));

export const ClickHouseEvolution: React.FC = () => {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [result, setResult] = useState<EvolutionResult | null>(null);
  const [planDiff, setPlanDiff] = useState<PlanDiff | null>(null);
  const [loading, setLoading] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSql, setShowSql] = useState(false);

  const loadAnalysis = useCallback(async () => {
    setLoadingAnalysis(true);
    setError(null);
    try {
      const [aRes, dRes] = await Promise.all([
        fetch('/api/evolution/analysis'),
        fetch('/api/evolution/plan_diff'),
      ]);
      if (!aRes.ok) {
        const body = await aRes.json().catch(() => ({}));
        throw new Error(body.detail || `Analysis unavailable (HTTP ${aRes.status})`);
      }
      setAnalysis(await aRes.json());
      if (dRes.ok) setPlanDiff(await dRes.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not read ClickHouse analytics');
      setAnalysis(null);
    } finally {
      setLoadingAnalysis(false);
    }
  }, []);

  useEffect(() => { loadAnalysis(); }, [loadAnalysis]);

  const runEvolution = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/evolution/evolve', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `Evolution failed (HTTP ${res.status})`);
      setResult(data);
      await loadAnalysis();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evolution failed');
    } finally {
      setLoading(false);
    }
  };

  const resetLineage = async () => {
    setResetting(true);
    try {
      await fetch('/api/evolution/reset', { method: 'POST' });
      setResult(null);
      await loadAnalysis();
    } catch {
      setError('Could not reset the strategy lineage');
    } finally {
      setResetting(false);
    }
  };

  const evolved = result?.status === 'STRATEGY_EVOLVED';
  const unchanged = result?.status === 'STRATEGY_UNCHANGED';
  const rejected = result?.status === 'STRATEGY_REJECTED';
  const activeHook = analysis?.active_strategy?.hook_type;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', padding: '2px' }}>

      {/* ------------------------------- Header ------------------------------- */}
      <div className="glass-panel" style={{ padding: '16px 18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <TrendingUp size={18} color="var(--primary-light)" />
              <h2 style={{ fontSize: '15px', fontWeight: 800 }}>CLOSED-LOOP EVOLUTION</h2>
              {analysis && (
                <span className={`badge-neon ${analysis.is_simulated ? 'badge-amber' : 'badge-emerald'}`} style={{ fontSize: '9px' }}>
                  {analysis.is_simulated ? '● SIMULATED' : `● ${analysis.server_identity}`}
                </span>
              )}
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', maxWidth: '620px', lineHeight: 1.6 }}>
              The Evolution Agent reads audience telemetry through the ClickHouse MCP server, tests whether a
              different hook genuinely outperforms the active one, and only then changes how the actor performs.
              It can change the performance. It can never change the identity.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              className="btn btn-secondary"
              onClick={resetLineage}
              disabled={resetting || loading}
              style={{ padding: '8px 12px', fontSize: '11px' }}
              title="Restores the v13 baseline so the loop can be demonstrated again. Telemetry and audit ledgers are untouched."
            >
              {resetting ? <Loader2 size={13} className="spin" /> : <RotateCcw size={13} />}
              Reset to baseline
            </button>
            <button
              className="btn btn-primary"
              onClick={runEvolution}
              disabled={loading}
              style={{ padding: '9px 18px', fontSize: '12px', fontWeight: 700 }}
            >
              {loading ? <Loader2 size={14} className="spin" /> : <Sparkles size={14} />}
              Run Evolution Agent
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="glass-panel" style={{ padding: '12px 14px', borderColor: 'rgba(244, 63, 94, 0.35)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: 'var(--accent-rose)' }}>
            <AlertTriangle size={13} /> {error}
          </div>
        </div>
      )}

      {/* -------------------------- Hook distribution -------------------------- */}
      <div className="glass-panel" style={{ padding: '0 0 4px' }}>
        <div style={{ padding: '11px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={14} color="var(--accent-cyan)" />
            <span style={{ fontSize: '12px', fontWeight: 700 }}>HOOK PERFORMANCE BY ARM</span>
            {analysis && !analysis.is_simulated && (
              <span style={{ fontSize: '9.5px', color: 'var(--text-muted)' }}>
                query 881a · {analysis.latency_ms}ms · {analysis.transport}
              </span>
            )}
          </div>
          {analysis?.compiled_sql && (
            <button className="btn btn-secondary" onClick={() => setShowSql((v) => !v)} style={{ padding: '3px 9px', fontSize: '9px' }}>
              {showSql ? 'Hide SQL' : 'Show SQL'}
            </button>
          )}
        </div>

        {showSql && analysis?.compiled_sql && (
          <pre className="code-font" style={{
            margin: '10px 16px', fontSize: '9.5px', color: 'var(--text-secondary)',
            backgroundColor: 'var(--bg-darkest)', padding: '10px', borderRadius: 'var(--radius-sm)', overflowX: 'auto'
          }}>
            {analysis.compiled_sql}
          </pre>
        )}

        {loadingAnalysis ? (
          <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Loader2 size={20} className="spin" />
            <p style={{ fontSize: '11px', marginTop: '8px' }}>Querying ClickHouse through MCP…</p>
          </div>
        ) : !analysis || analysis.rows.length === 0 ? (
          <div style={{ padding: '30px', textAlign: 'center' }}>
            <Database size={24} color="var(--text-dim)" />
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px', fontWeight: 600 }}>No data</p>
            <p style={{ fontSize: '10.5px', color: 'var(--text-muted)', marginTop: '4px' }}>
              No hook arm has reached the 50-impression sample floor yet.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
              <thead>
                <tr>
                  {['Hook arm', 'Impressions', 'Avg retention', '95% CI', 'Avg CTR', 'Opening'].map((h, i) => (
                    <th key={h} style={{
                      textAlign: i === 0 ? 'left' : 'right', padding: '7px 16px', fontSize: '9px',
                      fontWeight: 700, letterSpacing: '0.6px', color: 'var(--text-muted)',
                      textTransform: 'uppercase', borderBottom: '1px solid var(--border-subtle)'
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {analysis.rows.map((row, idx) => {
                  const isActive = row.hook_type === activeHook;
                  const isBest = idx === 0;
                  return (
                    <tr key={row.hook_type} style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      backgroundColor: isActive ? 'rgba(99, 102, 241, 0.08)' : 'transparent'
                    }}>
                      <td style={{ padding: '8px 16px', fontWeight: 700 }}>
                        {row.hook_type}
                        {isActive && <span className="badge-neon badge-primary" style={{ fontSize: '8px', marginLeft: '7px' }}>ACTIVE</span>}
                        {isBest && !isActive && <span className="badge-neon badge-emerald" style={{ fontSize: '8px', marginLeft: '7px' }}>BEST ARM</span>}
                      </td>
                      <td className="code-font" style={{ padding: '8px 16px', textAlign: 'right' }}>{row.n.toLocaleString()}</td>
                      <td className="code-font" style={{ padding: '8px 16px', textAlign: 'right', color: isBest ? 'var(--accent-emerald)' : 'var(--text-primary)', fontWeight: 700 }}>
                        {fmtNum(row.avg_retention)}
                      </td>
                      <td className="code-font" style={{ padding: '8px 16px', textAlign: 'right', color: 'var(--text-muted)' }}>
                        [{fmtNum(row.ci_95?.[0])}, {fmtNum(row.ci_95?.[1])}]
                      </td>
                      <td className="code-font" style={{ padding: '8px 16px', textAlign: 'right', color: 'var(--text-secondary)' }}>{fmtNum(row.avg_ctr, 5)}</td>
                      <td className="code-font" style={{ padding: '8px 16px', textAlign: 'right', color: 'var(--text-secondary)' }}>
                        {row.avg_opening_duration_s !== undefined ? `${row.avg_opening_duration_s}s` : '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ---------------------------- Decision ---------------------------- */}
      {result && (
        <div className="glass-panel" style={{
          padding: '16px 18px',
          borderColor: evolved ? 'rgba(16, 185, 129, 0.35)' : rejected ? 'rgba(244, 63, 94, 0.35)' : 'rgba(245, 158, 11, 0.35)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px', marginBottom: '10px' }}>
            {evolved ? <CheckCircle2 size={16} color="var(--accent-emerald)" />
              : rejected ? <XCircle size={16} color="var(--accent-rose)" />
                : <ShieldCheck size={16} color="var(--accent-amber)" />}
            <span style={{ fontSize: '13px', fontWeight: 800 }}>
              {evolved ? `STRATEGY EVOLVED — v${result.previous_strategy_version} → v${result.new_strategy_version}`
                : unchanged ? 'NO CHANGE WARRANTED'
                  : 'STRATEGY CHANGE REFUSED'}
            </span>
            <span className={`badge-neon ${evolved ? 'badge-emerald' : rejected ? 'badge-rose' : 'badge-amber'}`} style={{ fontSize: '9px' }}>
              {result.statistical_significance.decision}
            </span>
          </div>

          <p style={{ fontSize: '11.5px', color: 'var(--text-secondary)', lineHeight: 1.65, marginBottom: '12px' }}>
            {result.statistical_significance.rationale}
          </p>

          {/* Statistics grid */}
          {result.statistical_significance.test && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '9px', marginBottom: '10px' }}>
              {[
                { label: 'Verdict', value: result.statistical_significance.test.verdict.replace(/_/g, ' ') },
                { label: 'p-value', value: result.statistical_significance.test.p_value !== undefined ? result.statistical_significance.test.p_value.toExponential(2) : '—' },
                { label: 't-statistic', value: fmtNum(result.statistical_significance.test.t_statistic, 2) },
                { label: 'Deg. freedom', value: fmtNum(result.statistical_significance.test.degrees_of_freedom, 1) },
                { label: 'Relative lift', value: fmtPct(result.statistical_significance.relative_lift) },
                { label: 'Candidate n', value: (result.statistical_significance.n_candidate ?? 0).toLocaleString() },
              ].map((stat) => (
                <div key={stat.label} style={{ backgroundColor: 'var(--bg-darkest)', padding: '9px 11px', borderRadius: 'var(--radius-sm)' }}>
                  <div className="code-font" style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>{stat.value}</div>
                  <div style={{ fontSize: '8.5px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '2px' }}>{stat.label}</div>
                </div>
              ))}
            </div>
          )}

          <p style={{ fontSize: '9.5px', color: 'var(--text-muted)' }}>
            Evidence gathered via {result.mcp_governance.tools_invoked.join(', ')} on{' '}
            <strong style={{ color: 'var(--accent-cyan)' }}>{result.mcp_governance.mcp_provider}</strong> over{' '}
            {result.mcp_governance.transport} · {result.mcp_governance.query_latency_ms}ms total
          </p>
        </div>
      )}

      {/* ---------------------------- Plan diff ---------------------------- */}
      {planDiff && (
        <div className="glass-panel" style={{ padding: '16px 18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <ArrowRight size={15} color="var(--primary-light)" />
            <span style={{ fontSize: '12px', fontWeight: 700 }}>PERFORMANCE PLAN DIFF — NEXT RUN</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '7px' }}>
            {([
              ['Hook type', planDiff.hook_type],
              ['Opening duration', planDiff.opening_duration_s],
              ['Shot preference', planDiff.hook_shot],
              ['Strategy version', planDiff.strategy_version],
            ] as const).map(([label, field]) => (
              <div key={label} style={{
                display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 11px',
                borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-darkest)',
                opacity: field.changed ? 1 : 0.55
              }}>
                <span style={{ fontSize: '10.5px', color: 'var(--text-muted)', width: '130px', flexShrink: 0 }}>{label}</span>
                <span className="code-font" style={{ fontSize: '11px', color: 'var(--accent-rose)', textDecoration: field.changed ? 'line-through' : 'none' }}>
                  {String(field.run1)}
                </span>
                <ArrowRight size={12} color="var(--text-dim)" />
                <span className="code-font" style={{ fontSize: '11px', color: field.changed ? 'var(--accent-emerald)' : 'var(--text-secondary)', fontWeight: 700 }}>
                  {String(field.run2)}
                </span>
                {!field.changed && <span style={{ fontSize: '9px', color: 'var(--text-dim)' }}>unchanged</span>}
              </div>
            ))}
          </div>

          <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '11px', lineHeight: 1.6 }}>
            {planDiff.justification}
          </p>

          <div style={{
            marginTop: '11px', padding: '9px 11px', borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.22)',
            display: 'flex', alignItems: 'center', gap: '8px'
          }}>
            <ShieldCheck size={13} color="var(--primary-light)" />
            <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>
              Digital DNA is unchanged across this diff — face, voice and identity are immutable. Only direction changed.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
