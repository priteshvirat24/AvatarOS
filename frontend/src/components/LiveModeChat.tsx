import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Zap,
  Shield,
  Sparkles,
  Terminal,
  Mic,
  MicOff,
  Square,
  Play,
  Volume2,
  Radio,
  Activity,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  Cpu,
  Layers
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GoogleLabs3D } from './GoogleLabs3D';

interface TranscriptItem {
  speaker: 'user' | 'assistant';
  text: string;
  is_partial?: boolean;
  latency_ms?: number;
  latency_breakdown?: {
    asr_ms?: number;
    llm_ttft_ms?: number;
    audio_ttfa_ms?: number;
    total_latency_ms?: number;
  };
  register?: string;
  is_deflection?: boolean;
  timestamp?: string;
}

type AvatarState = 'IDLE' | 'LISTENING' | 'THINKING' | 'SPEAKING' | 'INTERRUPTED' | 'CLOSED';

interface LiveModeChatProps {
  onHandoffToStudio?: (draftBrief: string) => void;
}

export const LiveModeChat: React.FC<LiveModeChatProps> = ({ onHandoffToStudio }) => {
  // Session State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [handoffDraftMsg, setHandoffDraftMsg] = useState<string | null>(null);
  const [isHandoffLoading, setIsHandoffLoading] = useState(false);
  const [sessionStatus, setSessionStatus] = useState<AvatarState>('IDLE');
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [providerInfo, setProviderInfo] = useState<{
    provider: string;
    model: string;
    ready: boolean;
    degraded_mode?: boolean;
    is_realtime?: boolean;
  }>({
    provider: 'deterministic_fallback',
    model: 'deterministic-offline-v1',
    ready: true,
    degraded_mode: false,
    is_realtime: false
  });

  // Communication Strategy (Session-scoped adaptation)
  const [activeStrategy, setActiveStrategy] = useState({
    audience: 'General Developer',
    technical_depth: 'High',
    vocabulary: 'Technical',
    register: 'technical'
  });

  // Transcripts & Input
  const [transcripts, setTranscripts] = useState<TranscriptItem[]>([
    {
      speaker: 'assistant',
      text: "Hello! I'm Maya v1.7, your real-time digital advocate. Live conversational mode is active with memory isolation and sub-800ms latency.",
      register: 'technical',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isMicActive, setIsMicActive] = useState(false);
  const [micVolume, setMicVolume] = useState(0);

  // Latency & Telemetry
  const [lastMetrics, setLastMetrics] = useState({
    asr_ms: 110,
    llm_ttft_ms: 240,
    audio_ttfa_ms: 130,
    total_ms: 480,
    turn_count: 1,
    interruption_count: 0
  });

  // Audio & WebSocket Refs
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const transcriptScrollRef = useRef<HTMLDivElement>(null);

  // Fetch health/provider status on mount
  useEffect(() => {
    fetch('/health')
      .then((r) => r.json())
      .then((data) => {
        if (data.services?.live) {
          setProviderInfo({
            provider: data.services.live.provider || 'deterministic_fallback',
            model: data.services.live.model || 'deterministic-offline-v1',
            ready: data.services.live.ready ?? true,
            degraded_mode: data.services.live.degraded_mode ?? false,
            is_realtime: data.services.live.is_realtime ?? false
          });
        }
      })
      .catch(() => {});
  }, []);


  // Auto-scroll transcripts
  useEffect(() => {
    if (transcriptScrollRef.current) {
      transcriptScrollRef.current.scrollTop = transcriptScrollRef.current.scrollHeight;
    }
  }, [transcripts, sessionStatus]);

  // Start Live Session
  const startLiveSession = async (selectedLang: 'en' | 'hi' = language) => {
    try {
      setSessionStatus('LISTENING');
      const res = await fetch('/api/live/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: 'maya',
          language: selectedLang,
          enable_audio: true
        })
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setLanguage(selectedLang);
      setSessionStatus('LISTENING');

      // Update provider info from created session
      if (data.provider) {
        setProviderInfo((prev) => ({
          ...prev,
          provider: data.provider,
          model: data.model || (data.provider.includes('mistral') ? 'mistral-small-latest' : 'gemini-2.5-flash'),
          degraded_mode: data.degraded_mode ?? false,
          is_realtime: data.is_realtime ?? false,
          ready: true
        }));
      }

      // Connect WebSocket for real-time streaming
      connectWebSocket(data.session_id);
    } catch (e) {
      console.error('Failed to start Live Session:', e);
      setSessionStatus('IDLE');
    }
  };

  // Close Live Session
  const closeLiveSession = async () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    stopMic();

    if (sessionId) {
      try {
        await fetch(`/api/live/session/${sessionId}/close`, { method: 'POST' });
      } catch (e) {
        console.error(e);
      }
    }
    setSessionStatus('CLOSED');
    // Reset temporary session strategy
    setActiveStrategy({
      audience: 'General Developer',
      technical_depth: 'High',
      vocabulary: 'Technical',
      register: 'technical'
    });
  };

  // Connect WebSocket
  const connectWebSocket = (sid: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${window.location.host}/ws/live/${sid}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Live Mode WebSocket connected to:', wsUrl);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleWebSocketEvent(msg);
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    ws.onerror = (e) => {
      console.warn('WebSocket error, falling back to REST turns:', e);
    };

    ws.onclose = () => {
      console.log('Live Mode WebSocket closed');
    };

    wsRef.current = ws;
  };

  // Handle incoming WS events
  const handleWebSocketEvent = (msg: any) => {
    if (msg.type === 'transcript') {
      const turn = msg.turn;
      if (!turn.is_partial) {
        setTranscripts((prev) => [
          ...prev,
          {
            speaker: turn.speaker,
            text: turn.text,
            is_partial: false,
            timestamp: new Date().toLocaleTimeString()
          }
        ]);
      }
    } else if (msg.type === 'response_chunk') {
      setSessionStatus('SPEAKING');
      // Update or append streaming assistant chunk
      setTranscripts((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.speaker === 'assistant' && last.is_partial) {
          return [
            ...prev.slice(0, -1),
            { ...last, text: last.text + msg.text }
          ];
        } else {
          return [
            ...prev,
            {
              speaker: 'assistant',
              text: msg.text,
              is_partial: true,
              timestamp: new Date().toLocaleTimeString()
            }
          ];
        }
      });
    } else if (msg.type === 'response_complete') {
      setSessionStatus('LISTENING');
      // Finalize partial chunk
      setTranscripts((prev) => {
        const last = prev[prev.length - 1];
        if (last && last.speaker === 'assistant') {
          return [
            ...prev.slice(0, -1),
            { ...last, text: msg.full_text, is_partial: false }
          ];
        }
        return prev;
      });
    } else if (msg.type === 'interrupted') {
      setSessionStatus('INTERRUPTED');
      setLastMetrics((prev) => ({
        ...prev,
        interruption_count: prev.interruption_count + 1
      }));
      setTimeout(() => setSessionStatus('LISTENING'), 1200);
    }
  };

  // Send a Turn (Text or Voice)
  const sendTurn = async (text: string) => {
    if (!text.trim()) return;

    // If session not active, start it first
    let activeSid = sessionId;
    if (!activeSid || sessionStatus === 'CLOSED' || sessionStatus === 'IDLE') {
      try {
        const res = await fetch('/api/live/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ character_id: 'maya', language })
        });
        const data = await res.json();
        activeSid = data.session_id;
        setSessionId(activeSid);
        connectWebSocket(data.session_id);
      } catch (e) {
        console.error(e);
        return;
      }
    }

    // Add User Transcript
    const userItem: TranscriptItem = {
      speaker: 'user',
      text,
      timestamp: new Date().toLocaleTimeString()
    };
    setTranscripts((prev) => [...prev, userItem]);
    setInputValue('');
    setSessionStatus('THINKING');

    // Adapt session strategy badge based on turn intent
    const lower = text.toLowerCase();
    if (lower.includes('beginner') || lower.includes('12-year-old')) {
      setActiveStrategy({
        audience: '12-Year-Old Student',
        technical_depth: 'Low',
        vocabulary: 'Simple',
        register: 'beginner'
      });
    } else if (lower.includes('cto') || lower.includes('enterprise')) {
      setActiveStrategy({
        audience: 'Enterprise CTO',
        technical_depth: 'Maximum',
        vocabulary: 'Advanced/Architectural',
        register: 'enterprise'
      });
    } else if (lower.includes('political') || lower.includes('financial')) {
      // Restricted
    } else {
      setActiveStrategy({
        audience: 'General Developer',
        technical_depth: 'High',
        vocabulary: 'Technical',
        register: 'technical'
      });
    }

    try {
      const res = await fetch(`/api/live/session/${activeSid}/turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();

      setSessionStatus('SPEAKING');

      // Update metrics
      const bk = data.latency_breakdown || {
        asr_latency_ms: 110,
        time_to_first_token_ms: 240,
        time_to_first_audio_ms: 130,
        total_latency_ms: 480
      };

      setLastMetrics({
        asr_ms: bk.asr_latency_ms,
        llm_ttft_ms: bk.time_to_first_token_ms,
        audio_ttfa_ms: bk.time_to_first_audio_ms,
        total_ms: bk.total_latency_ms,
        turn_count: data.turn_count || lastMetrics.turn_count + 1,
        interruption_count: lastMetrics.interruption_count
      });

      // Append Assistant Transcript
      setTranscripts((prev) => [
        ...prev,
        {
          speaker: 'assistant',
          text: data.reply_text,
          latency_ms: bk.total_latency_ms,
          latency_breakdown: {
            asr_ms: bk.asr_latency_ms,
            llm_ttft_ms: bk.time_to_first_token_ms,
            audio_ttfa_ms: bk.time_to_first_audio_ms,
            total_latency_ms: bk.total_latency_ms
          },
          register: activeStrategy.register,
          is_deflection: data.reply_text.includes("I cannot provide") || data.reply_text.includes("restricted"),
          timestamp: new Date().toLocaleTimeString()
        }
      ]);

      // Return to listening after short speaking duration
      setTimeout(() => {
        setSessionStatus('LISTENING');
      }, 2500);

    } catch (e) {
      console.error('Turn processing failed:', e);
      setSessionStatus('IDLE');
    }
  };

  // Barge-in / Interruption Handler
  const handleInterrupt = async () => {
    if (!sessionId) return;
    setSessionStatus('INTERRUPTED');

    // Notify backend
    try {
      await fetch(`/api/live/session/${sessionId}/interrupt`, { method: 'POST' });
    } catch (e) {
      console.error(e);
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt' }));
    }

    setLastMetrics((prev) => ({
      ...prev,
      interruption_count: prev.interruption_count + 1
    }));

    setTranscripts((prev) => [
      ...prev,
      {
        speaker: 'assistant',
        text: '⚡ [RESPONSE INTERRUPTED BY USER BARGE-IN]',
        register: 'interrupted',
        timestamp: new Date().toLocaleTimeString()
      }
    ]);

    setTimeout(() => setSessionStatus('LISTENING'), 800);
  };

  // Microphone Audio Capture
  const toggleMic = async () => {
    if (isMicActive) {
      stopMic();
    } else {
      await startMic();
    }
  };

  const startMic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      setIsMicActive(true);
      if (sessionStatus === 'IDLE' || sessionStatus === 'CLOSED') {
        startLiveSession(language);
      }

      // Visualizer loop
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      const updateVolume = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setMicVolume(Math.min(100, Math.round((avg / 255) * 100)));
        animFrameRef.current = requestAnimationFrame(updateVolume);
      };
      updateVolume();
    } catch (e) {
      console.warn('Microphone permission denied or not supported:', e);
      setIsMicActive(false);
    }
  };

  const stopMic = () => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setIsMicActive(false);
    setMicVolume(0);
  };

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '440px 1fr',
      height: '100%',
      backgroundColor: 'var(--bg-darkest)',
      gap: '16px',
      padding: '20px',
      overflow: 'hidden'
    }}>
      {/* Left Column: Live Stage & Avatar Visualizer */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
        {/* Avatar Visualizer Panel */}
        <div className="glass-panel" style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          position: 'relative',
          overflow: 'hidden',
          backgroundColor: '#000',
          border: '1px solid var(--border-focus)'
        }}>
          {/* Top HUD: DNA Sealing & Character Version */}
          <div style={{
            position: 'absolute',
            top: '14px',
            left: '16px',
            right: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            zIndex: 10
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div className="status-dot active" />
              <span style={{ fontSize: '11px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
                MAYA v1.7.0 (LOCKED)
              </span>
            </div>
            <span className="badge-neon badge-emerald" style={{ fontSize: '9px' }}>
              READ-ONLY DNA
            </span>
          </div>

          {/* 3D Google Labs Hologram Visualizer */}
          <div style={{
            position: 'relative',
            width: '100%',
            height: '240px',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            marginTop: '28px'
          }}>
            <GoogleLabs3D
              characterName="Maya"
              characterVersion="v1.7.0"
              isSpeaking={sessionStatus === 'SPEAKING'}
              isListening={sessionStatus === 'LISTENING' || isMicActive}
              energy={micVolume > 10 ? (micVolume / 100) * 1.5 : 0.78}
              height="100%"
            />

            {/* Status Floating Pill */}
            <div style={{
              position: 'absolute',
              bottom: '12px',
              left: '50%',
              transform: 'translateX(-50%)',
              padding: '4px 14px',
              borderRadius: '9999px',
              backgroundColor: 'rgba(19,19,20,0.92)',
              border: '1px solid var(--border-subtle)',
              fontSize: '10px',
              fontWeight: 800,
              letterSpacing: '1px',
              fontFamily: 'var(--font-mono)',
              color:
                sessionStatus === 'SPEAKING' ? 'var(--color-primary)' :
                sessionStatus === 'THINKING' ? 'var(--accent-cyan)' :
                sessionStatus === 'INTERRUPTED' ? 'var(--color-error)' :
                'var(--color-secondary)',
              zIndex: 10
            }}>
              {sessionStatus}
            </div>
          </div>

          {/* Dynamic Audio Visualizer Wavebars */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            height: '24px',
            marginTop: '36px'
          }}>
            {[40, 75, 100, 60, 85, 30, 95, 50, 80, 45, 70, 30].map((h, i) => (
              <div
                key={i}
                style={{
                  width: '3px',
                  height: sessionStatus === 'SPEAKING'
                    ? `${Math.max(6, (h / 100) * 24)}px`
                    : isMicActive
                    ? `${Math.max(4, (micVolume / 100) * 24 * (h / 100))}px`
                    : '4px',
                  backgroundColor: sessionStatus === 'SPEAKING'
                    ? 'var(--primary-light)'
                    : isMicActive
                    ? 'var(--accent-emerald)'
                    : 'var(--text-dim)',
                  borderRadius: '2px',
                  transition: 'height 0.1s ease'
                }}
              />
            ))}
          </div>

          {/* Bottom Latency Budget Indicator */}
          <div style={{
            position: 'absolute',
            bottom: '12px',
            left: '16px',
            right: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '11px',
            color: 'var(--text-muted)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-emerald)' }}>
              <Zap size={12} />
              <span style={{ fontWeight: 700 }}>{lastMetrics.total_ms}ms</span>
              <span style={{ fontSize: '9px', color: 'var(--text-muted)' }}>(target &lt;800ms)</span>
            </div>
            <div style={{ fontSize: '9px', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
              ASR: {lastMetrics.asr_ms}ms | TTFT: {lastMetrics.llm_ttft_ms}ms | TTS: {lastMetrics.audio_ttfa_ms}ms
            </div>
          </div>
        </div>

        {/* Session-Scoped Adaptation Controls */}
        <div className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.5px' }}>
              SESSION-SCOPED COMMUNICATION STRATEGY
            </span>
            <span className="badge-neon badge-cyan" style={{ fontSize: '9px' }}>
              {activeStrategy.register.toUpperCase()}
            </span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '8px',
            fontSize: '11px',
            backgroundColor: 'var(--bg-darkest)',
            padding: '10px',
            borderRadius: 'var(--radius-sm)'
          }}>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Target Audience:</span>
              <div style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{activeStrategy.audience}</div>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Technical Depth:</span>
              <div style={{ fontWeight: 700, color: 'var(--accent-amber)' }}>{activeStrategy.technical_depth}</div>
            </div>
          </div>

          {/* Quick Register Adaptation Triggers */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
            <button
              className="btn btn-secondary"
              style={{ fontSize: '10px', padding: '6px 8px', justifyContent: 'flex-start' }}
              onClick={() => sendTurn("Explain our developer platform architecture.")}
            >
              <Terminal size={11} color="var(--primary-light)" />
              1. Technical (Default)
            </button>

            <button
              className="btn btn-secondary"
              style={{ fontSize: '10px', padding: '6px 8px', justifyContent: 'flex-start' }}
              onClick={() => sendTurn("Too technical. Explain it to a 12-year-old beginner.")}
            >
              <Sparkles size={11} color="var(--accent-amber)" />
              2. 12-Year-Old Beginner
            </button>

            <button
              className="btn btn-secondary"
              style={{ fontSize: '10px', padding: '6px 8px', justifyContent: 'flex-start' }}
              onClick={() => sendTurn("Now explain it to an enterprise CTO.")}
            >
              <Shield size={11} color="var(--accent-cyan)" />
              3. Enterprise CTO
            </button>

            <button
              className="btn btn-danger"
              style={{ fontSize: '10px', padding: '6px 8px', justifyContent: 'flex-start' }}
              onClick={() => sendTurn("Give me political endorsement advice.")}
            >
              <AlertTriangle size={11} />
              4. Test Deflection
            </button>
          </div>

          <div style={{ fontSize: '9px', color: 'var(--text-dim)', lineHeight: 1.3 }}>
            * Note: Temporary session state disappears at session close. Core Digital DNA is never modified.
          </div>
        </div>
      </div>

      {/* Right Column: Live Conversation & Telemetry */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%', overflow: 'hidden' }}>
        {/* Top Header & Controls */}
        <div className="glass-panel" style={{
          padding: '12px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Radio size={18} color="var(--primary-light)" />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 800 }}>
                  {providerInfo.provider.includes('gemini')
                    ? 'GEMINI LIVE REAL-TIME RUNTIME'
                    : (providerInfo.provider.includes('mistral')
                        ? 'MISTRAL CONVERSATIONAL RUNTIME (TURN-BASED)'
                        : 'LIVE CONVERSATIONAL RUNTIME (OFFLINE)')}
                </span>
                <span
                  className={`badge-neon ${
                    providerInfo.provider.includes('gemini')
                      ? 'badge-primary'
                      : (providerInfo.provider.includes('mistral')
                          ? 'badge-amber'
                          : 'badge-amber')
                  }`}
                  style={{ fontSize: '9px' }}
                >
                  {providerInfo.provider.includes('gemini')
                    ? '● REALTIME GEMINI LIVE'
                    : (providerInfo.provider.includes('mistral')
                        ? '● DEGRADED MISTRAL TURN-BASED'
                        : '● OFFLINE FALLBACK')}
                </span>
              </div>
              <p style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                Session ID: {sessionId ? sessionId.slice(0, 16) + '...' : 'None (Click Start)'} | Trace: active
              </p>
            </div>
          </div>

          {/* Language Toggle & Session Control */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ display: 'flex', backgroundColor: 'var(--bg-darkest)', padding: '2px', borderRadius: 'var(--radius-sm)' }}>
              <button
                onClick={() => { setLanguage('en'); if (sessionId) startLiveSession('en'); }}
                style={{
                  padding: '4px 8px',
                  fontSize: '10px',
                  fontWeight: 700,
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: language === 'en' ? 'var(--primary)' : 'transparent',
                  color: language === 'en' ? 'white' : 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                EN
              </button>
              <button
                onClick={() => { setLanguage('hi'); if (sessionId) startLiveSession('hi'); }}
                style={{
                  padding: '4px 8px',
                  fontSize: '10px',
                  fontWeight: 700,
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: language === 'hi' ? 'var(--accent-emerald)' : 'transparent',
                  color: language === 'hi' ? 'white' : 'var(--text-muted)',
                  cursor: 'pointer'
                }}
              >
                HI (Hindi)
              </button>
            </div>

            {sessionId && sessionStatus !== 'CLOSED' ? (
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '11px', padding: '6px 10px', borderColor: 'var(--primary-light)', color: 'var(--primary-light)' }}
                  disabled={isHandoffLoading}
                  onClick={async () => {
                    setIsHandoffLoading(true);
                    try {
                      const res = await fetch(`/api/live/session/${sessionId}/handoff`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          session_id: sessionId,
                          target_audience: activeStrategy.audience || 'technical'
                        })
                      });
                      const data = await res.json();
                      setHandoffDraftMsg(data.draft_brief);
                      if (onHandoffToStudio) {
                        onHandoffToStudio(data.draft_brief);
                      }
                    } catch (e) {
                      console.error("Handoff error:", e);
                    } finally {
                      setIsHandoffLoading(false);
                    }
                  }}
                  title="Synthesize conversation into a Studio production draft without promoting session memory"
                >
                  <Sparkles size={12} />
                  {isHandoffLoading ? 'Synthesizing...' : 'Handoff to Studio'}
                </button>
                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '11px', padding: '6px 12px' }}
                  onClick={closeLiveSession}
                >
                  <Square size={12} color="var(--accent-rose)" />
                  End Session
                </button>
              </div>
            ) : (
              <button
                className="btn btn-primary"
                style={{ fontSize: '11px', padding: '6px 14px' }}
                onClick={() => startLiveSession(language)}
              >
                <Play size={12} />
                Start Live Session
              </button>
            )}
          </div>
        </div>

        {/* Safe Handoff Banner (Milestone 9, Section 24) */}
        {handoffDraftMsg && (
          <div style={{
            padding: '10px 14px',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid var(--border-focus)',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 700, color: 'var(--primary-light)' }}>
                <CheckCircle2 size={13} />
                <span>LIVE → STUDIO DRAFT SYNTHESIZED</span>
              </div>
              <span className="badge-neon badge-cyan" style={{ fontSize: '9px' }}>
                MEMORY ISOLATED (NOT PROMOTED)
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
              {handoffDraftMsg}
            </p>
          </div>
        )}

        {/* Transcripts Scroll Area */}
        <div
          ref={transcriptScrollRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            padding: '12px',
            backgroundColor: 'var(--bg-base)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)'
          }}
        >
          {transcripts.map((t, idx) => {
            const isMaya = t.speaker === 'assistant';
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: isMaya ? 'flex-start' : 'flex-end'
                }}
              >
                <div style={{
                  maxWidth: '80%',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: isMaya ? 'var(--bg-surface-elevated)' : 'var(--primary)',
                  border: isMaya
                    ? t.is_deflection
                      ? '1px solid var(--accent-amber)'
                      : '1px solid var(--border-subtle)'
                    : 'none',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  lineHeight: 1.5
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginBottom: '4px',
                    fontSize: '10px',
                    fontWeight: 700,
                    color: isMaya ? 'var(--primary-light)' : 'rgba(255,255,255,0.8)'
                  }}>
                    <span>{isMaya ? 'MAYA v1.7.0' : 'YOU'}</span>
                    {t.register && (
                      <span className="badge-neon badge-cyan" style={{ fontSize: '8px', padding: '1px 5px' }}>
                        {t.register}
                      </span>
                    )}
                    {t.is_deflection && (
                      <span className="badge-neon badge-amber" style={{ fontSize: '8px', padding: '1px 5px' }}>
                        DEFLECTED
                      </span>
                    )}
                    {t.is_partial && (
                      <span className="badge-neon badge-emerald" style={{ fontSize: '8px', padding: '1px 5px' }}>
                        STREAMING...
                      </span>
                    )}
                    {t.latency_ms && (
                      <span style={{ fontSize: '10px', color: 'var(--accent-emerald)', marginLeft: 'auto' }}>
                        {t.latency_ms}ms
                      </span>
                    )}
                    {t.timestamp && (
                      <span style={{ fontSize: '9px', color: 'var(--text-dim)', marginLeft: t.latency_ms ? '6px' : 'auto' }}>
                        {t.timestamp}
                      </span>
                    )}
                  </div>
                  {t.text}
                </div>
              </div>
            );
          })}
        </div>

        {/* Input Bar & Barge-in Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            {/* Microphone Toggle Button */}
            <button
              onClick={toggleMic}
              className={`btn ${isMicActive ? 'btn-danger' : 'btn-secondary'}`}
              style={{ padding: '0 14px' }}
              title={isMicActive ? 'Mute Microphone' : 'Activate Live Microphone'}
            >
              {isMicActive ? <MicOff size={16} /> : <Mic size={16} />}
              <span style={{ fontSize: '11px' }}>{isMicActive ? `${micVolume}%` : 'Mic'}</span>
            </button>

            {/* Barge-In / Interrupt Button */}
            <button
              onClick={handleInterrupt}
              className="btn btn-secondary"
              style={{
                borderColor: 'var(--accent-rose)',
                color: 'var(--accent-rose)',
                fontSize: '11px',
                padding: '0 12px'
              }}
              title="Immediately stop Maya's current response"
            >
              <Zap size={13} color="var(--accent-rose)" />
              Barge-in
            </button>

            {/* Text Input Form */}
            <form
              onSubmit={(e) => { e.preventDefault(); sendTurn(inputValue); }}
              style={{ display: 'flex', gap: '8px', flex: 1 }}
            >
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Talk to Maya (ask a question or request a style change)..."
                style={{
                  flex: 1,
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 16px',
                  color: 'white',
                  fontFamily: 'var(--font-body)',
                  fontSize: '13px',
                  outline: 'none'
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = 'var(--border-focus)'}
                onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
              />
              <button
                type="submit"
                className="btn btn-primary"
                style={{ padding: '0 18px' }}
              >
                <Send size={14} />
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
