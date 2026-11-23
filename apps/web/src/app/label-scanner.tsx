"use client";

import { FormEvent, useState } from "react";
import { readLabelOnDevice } from "./label-ocr";

type Observation = {
  product_name?: string | null;
  brand?: string | null;
  visible_ingredients?: string[];
  visible_warnings?: string[];
  uncertain_text?: string[];
};
type ProviderResult = { status: string; message: string; observation: Observation | null };
type ScanResult =
  | { kind: "gemini"; message: string; observation: Observation }
  | { kind: "device"; text: string; fromFallback: boolean }
  | { kind: "error"; message: string };
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const acceptedImages = ["image/jpeg", "image/png", "image/webp"];

function ScanResultView({ result }: { result: ScanResult }) {
  if (result.kind === "error") {
    return <div className="label-result" role="status">
      <strong>Couldn’t read the label</strong>
      <p>{result.message}</p>
    </div>;
  }
  if (result.kind === "device") {
    return <div className="label-result" role="status">
      <strong>Text read on your device</strong>
      <p>{result.fromFallback && "The Gemini summary was unavailable. "}Check this reading against the package.</p>
      <p style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{result.text}</p>
    </div>;
  }

  const fields = [
    ["Product", result.observation.product_name || "Not legible"],
    ["Brand", result.observation.brand || "Not legible"],
    ["Ingredients", result.observation.visible_ingredients?.join(", ") || "Not legible"],
    ["Warnings", result.observation.visible_warnings?.join(", ") || "Not legible"],
    ["Uncertain text", result.observation.uncertain_text?.join(", ") || "None reported"],
  ];
  return <div className="label-result" role="status">
    <strong>Visible text — unverified</strong>
    <p>{result.message}</p>
    <dl>{fields.map(([label, value]) =>
      <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
  </div>;
}

async function readLabelWithGemini(file: File): Promise<ScanResult | null> {
  const form = new FormData();
  form.append("image", file);
  form.append("consent", "true");
  try {
    const response = await fetch(`${api}/api/v1/vision/label`, {
      method: "POST",
      body: form,
      signal: AbortSignal.timeout(48_000),
    });
    if (!response.ok) return null;
    const result: ProviderResult = await response.json();
    if (result.status === "observed_unverified" && result.observation) {
      return { kind: "gemini", message: result.message, observation: result.observation };
    }
  } catch {
    // An unavailable summary should still allow a local reading.
  }
  return null;
}

function useLabelScan() {
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);

  async function scan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || busy) return;
    if (!acceptedImages.includes(file.type) || file.size > 5_000_000) {
      setResult({ kind: "error", message: "Choose a JPEG, PNG or WebP photo up to 5 MB." });
      return;
    }
    setBusy(true);
    setResult(null);
    try {
      const summary = consent ? await readLabelWithGemini(file) : null;
      if (summary) {
        setResult(summary);
        return;
      }
      const text = await readLabelOnDevice(file);
      if (!text) throw new Error("No visible text");
      setResult({ kind: "device", text, fromFallback: consent });
    } catch {
      setResult({ kind: "error", message: "Try a sharper, closer photo of the English text, or type the label into a question." });
    } finally {
      setBusy(false);
    }
  }

  return { file, setFile, consent, setConsent, busy, result, setResult, scan };
}

export default function LabelScanner({ imageUrl }: { imageUrl?: string | null }) {
  const { file, setFile, consent, setConsent, busy, result, setResult, scan } = useLabelScan();
  return <section id="label" className="tool-section label-section" aria-labelledby="label-title">
    <div className="wrap">
      <h2 id="label-title">Read a product label.</h2>
      <div className="tool-split">
        <div className="tool-copy">
          <p>Photograph the ingredients or warnings panel. Read English text on your device and check it against the package.</p>
          <form className="label-form" onSubmit={scan} aria-busy={busy}>
            <div className="label-upload">
              <label htmlFor="label-image">Package photo</label>
              <input id="label-image" type="file" accept={acceptedImages.join(",")} disabled={busy} onChange={(event) => { setFile(event.target.files?.[0] || null); setResult(null); }} />
              <small>JPEG, PNG or WebP · up to 5 MB</small>
            </div>
            <label className="label-consent"><input type="checkbox" checked={consent} disabled={busy} onChange={(event) => setConsent(event.target.checked)} /> Optional. Send this photo to Gemini for an ingredient and warning summary.</label>
            <button className="primary-action" type="submit" disabled={!file || busy}>{busy ? "Reading…" : "Read label"} <span aria-hidden="true">↗</span></button>
            {result && <ScanResultView result={result} />}
          </form>
        </div>
        {imageUrl && <figure className="tool-visual label-visual">
          <img src={imageUrl} alt="Example Little Joys product packaging" width="600" height="600" loading="lazy" />
        </figure>}
      </div>
    </div>
  </section>;
}
