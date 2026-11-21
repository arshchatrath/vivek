function wavFile(samples: Float32Array) {
  const wave = new ArrayBuffer(44 + samples.length * 2);
  const header = new DataView(wave);
  const bytes = new Uint8Array(wave);
  const encoder = new TextEncoder();
  bytes.set(encoder.encode("RIFF"), 0);
  header.setUint32(4, wave.byteLength - 8, true);
  bytes.set(encoder.encode("WAVEfmt "), 8);
  header.setUint32(16, 16, true);
  header.setUint16(20, 1, true);
  header.setUint16(22, 1, true);
  header.setUint32(24, 16_000, true);
  header.setUint32(28, 32_000, true);
  header.setUint16(32, 2, true);
  header.setUint16(34, 16, true);
  bytes.set(encoder.encode("data"), 36);
  header.setUint32(40, samples.length * 2, true);
  samples.forEach((sample, i) => {
    const clamped = Math.max(-1, Math.min(1, sample));
    header.setInt16(44 + i * 2, Math.round(clamped * 32767), true);
  });
  return new Blob([wave], { type: "audio/wav" });
}

export async function recordVoice(signal: AbortSignal, ready: (stop: () => void) => void) {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder || !window.AudioContext) {
    throw new Error("Voice input requires a supported browser on HTTPS or localhost.");
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } });
  try {
    signal.throwIfAborted();
    const recorder = new MediaRecorder(stream);
    const chunks: Blob[] = [];
    const stop = () => {
      if (recorder.state === "recording") recorder.stop();
    };
    const clip = new Promise<Blob>((resolve, reject) => {
      recorder.ondataavailable = ({ data }) => chunks.push(data);
      recorder.onstop = () => resolve(new Blob(chunks, { type: recorder.mimeType }));
      recorder.onerror = () => reject(new Error("The microphone stopped unexpectedly."));
      recorder.start();
    });
    const timer = window.setTimeout(stop, 20_000);
    signal.addEventListener("abort", stop, { once: true });
    ready(stop);
    try {
      return await clip;
    } finally {
      window.clearTimeout(timer);
      signal.removeEventListener("abort", stop);
    }
  } finally {
    stream.getTracks().forEach((track) => track.stop());
  }
}

export async function recordingAsWav(clip: Blob) {
  if (!clip.size) throw new Error("No audio was recorded. Try again or type your concern.");
  const context = new AudioContext({ sampleRate: 16_000 });
  try {
    const audio = await context.decodeAudioData(await clip.arrayBuffer());
    return wavFile(audio.getChannelData(0).subarray(0, 320_000));
  } finally {
    await context.close();
  }
}
