'use client';

// Voice through Sarvam (spec G0): the mic records 16 kHz mono WAV for Saaras v4 speech-to-text, sent as the
// turn's `audio_b64`; answers are spoken with Bulbul v4 Flash from GET /v1/tts. The browser's own speech
// engines are only a fallback when Sarvam is unreachable.
import { apiGet } from '../api/client';

export type Recording = { stop: () => Promise<string | null>; cancel: () => void };

/** Start recording; `stop()` resolves to base64 WAV (null if nothing usable was recorded). */
export async function startRecording(): Promise<Recording> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream);
  const chunks: Blob[] = [];
  recorder.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  recorder.start();
  const release = () => stream.getTracks().forEach((t) => t.stop());
  return {
    cancel: () => {
      recorder.stop();
      release();
    },
    stop: () =>
      new Promise((resolve) => {
        recorder.onstop = async () => {
          release();
          const blob = new Blob(chunks, { type: recorder.mimeType });
          resolve(blob.size ? await toWavBase64(blob) : null);
        };
        recorder.stop();
      }),
  };
}

async function toWavBase64(blob: Blob): Promise<string | null> {
  const ctx = new AudioContext();
  try {
    const decoded = await ctx.decodeAudioData(await blob.arrayBuffer());
    const rate = 16000;
    const offline = new OfflineAudioContext(1, Math.max(1, Math.ceil(decoded.duration * rate)), rate);
    const source = offline.createBufferSource();
    source.buffer = decoded;
    source.connect(offline.destination);
    source.start();
    const pcm = (await offline.startRendering()).getChannelData(0);
    if (pcm.length < rate / 4) return null; // under a quarter second: a tap, not speech
    return base64(wav(pcm, rate));
  } catch {
    return null;
  } finally {
    void ctx.close();
  }
}

function wav(samples: Float32Array, rate: number): Uint8Array {
  const out = new DataView(new ArrayBuffer(44 + samples.length * 2));
  const text = (at: number, s: string) => [...s].forEach((c, i) => out.setUint8(at + i, c.charCodeAt(0)));
  text(0, 'RIFF');
  out.setUint32(4, 36 + samples.length * 2, true);
  text(8, 'WAVE');
  text(12, 'fmt ');
  out.setUint32(16, 16, true);
  out.setUint16(20, 1, true); // PCM
  out.setUint16(22, 1, true); // mono
  out.setUint32(24, rate, true);
  out.setUint32(28, rate * 2, true);
  out.setUint16(32, 2, true);
  out.setUint16(34, 16, true);
  text(36, 'data');
  out.setUint32(40, samples.length * 2, true);
  samples.forEach((s, i) => out.setInt16(44 + i * 2, Math.max(-1, Math.min(1, s)) * 0x7fff, true));
  return new Uint8Array(out.buffer);
}

function base64(bytes: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x8000)
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

let playing: HTMLAudioElement | null = null;

/** Speak an answer with Bulbul (Priya); resolves when playback ends. */
export async function speak(text: string, lang: string): Promise<void> {
  playing?.pause();
  try {
    const res = (await apiGet(`/v1/tts?text=${encodeURIComponent(text.slice(0, 500))}&lang=${lang}`)) as {
      audio_b64: string | null;
    };
    if (res.audio_b64) {
      const audio = new Audio(`data:audio/wav;base64,${res.audio_b64}`);
      playing = audio;
      await new Promise<void>((resolve) => {
        audio.onended = () => resolve();
        audio.onerror = () => resolve();
        void audio.play().catch(() => resolve());
      });
      return;
    }
  } catch {
    // Sarvam unreachable: the browser voice below keeps the answer audible
  }
  if ('speechSynthesis' in window) {
    await new Promise<void>((resolve) => {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = lang;
      u.onend = () => resolve();
      window.speechSynthesis.speak(u);
    });
  }
}
