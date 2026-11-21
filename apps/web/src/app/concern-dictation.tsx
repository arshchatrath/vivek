import { useEffect, useRef, useState } from "react";
import { recordVoice, recordingAsWav } from "./voice-recording";

const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const voiceUnavailable = "Voice input is unavailable. You can type your concern instead.";

async function transcribe(clip: Blob, signal: AbortSignal) {
  const audio = await recordingAsWav(clip);
  const form = new FormData();
  form.set("audio", audio, "concern.wav");
  form.set("consent", "true");
  const response = await fetch(`${api}/api/v1/speech/transcribe`, { method: "POST", body: form, signal });
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : voiceUnavailable);
  if (typeof data.transcript !== "string") throw new Error(voiceUnavailable);
  return data.transcript.trim();
}

function voiceError(error: unknown) {
  if (error instanceof DOMException && error.name === "NotAllowedError") {
    return "Microphone access was denied. Allow access or type your concern.";
  }
  if (error instanceof DOMException && error.name === "NotFoundError") {
    return "No microphone was found. You can type your concern instead.";
  }
  return error instanceof Error && !(error instanceof DOMException || error instanceof TypeError)
    ? error.message : voiceUnavailable;
}

export default function ConcernDictation({ disabled, onTranscript }: {
  disabled: boolean;
  onTranscript: (text: string) => void;
}) {
  const request = useRef<AbortController | null>(null);
  const stopRecording = useRef<(() => void) | null>(null);
  const [phase, setPhase] = useState<"idle" | "starting" | "recording" | "transcribing">("idle");
  const [message, setMessage] = useState("");

  useEffect(() => () => {
    request.current?.abort();
    request.current = null;
  }, []);

  useEffect(() => {
    if (disabled) request.current?.abort();
  }, [disabled]);

  async function dictate() {
    const controller = new AbortController();
    request.current = controller;
    setPhase("starting");
    setMessage("Waiting for microphone access…");
    try {
      const clip = await recordVoice(controller.signal, (stop) => {
        stopRecording.current = stop;
        setPhase("recording");
        setMessage("Recording… Tap Stop mic when you’re done.");
      });
      controller.signal.throwIfAborted();
      setPhase("transcribing");
      setMessage("Transcribing with Gnani…");
      const transcript = await transcribe(clip, controller.signal);
      controller.signal.throwIfAborted();
      if (transcript) onTranscript(transcript);
      setMessage(transcript ? "Voice text added. Check it before submitting." : "No speech was detected. Try again or type your concern.");
    } catch (error) {
      if (request.current === controller) setMessage(controller.signal.aborted ? "" : voiceError(error));
    } finally {
      if (request.current === controller) {
        request.current = null;
        stopRecording.current = null;
        setPhase("idle");
      }
    }
  }

  const recording = phase === "recording";
  function toggleMic() {
    if (recording) stopRecording.current?.();
    else if (!request.current) void dictate();
  }

  return <>
    <button type="button" className="dictation-button" onClick={toggleMic}
      disabled={disabled || phase === "starting" || phase === "transcribing"}
      aria-pressed={recording} aria-describedby="concern-mic-help">
      <span aria-hidden="true" />{recording ? "Stop mic" : "Use mic"}
    </button>
    <small className="dictation-status" role="status">{message}</small>
  </>;
}
