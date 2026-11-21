"use client";

import { FormEvent, useState } from "react";

type Observation = {
  product_name?: string | null;
  brand?: string | null;
  visible_ingredients?: string[];
  visible_warnings?: string[];
  uncertain_text?: string[];
};
type ScanResult = { status: string; message: string; observation: Observation | null };
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function ScanResultView({ result }: { result: ScanResult }) {
  const fields = [
    ["Product", result.observation?.product_name || "Not legible"],
    ["Brand", result.observation?.brand || "Not legible"],
    ["Ingredients", result.observation?.visible_ingredients?.join(", ") || "Not legible"],
    ["Warnings", result.observation?.visible_warnings?.join(", ") || "Not legible"],
    ["Uncertain text", result.observation?.uncertain_text?.join(", ") || "None reported"],
  ];
  return <div className="label-result" role="status">
    <strong>{result.status === "observed_unverified" ? "Visible text — unverified" : "Image reading unavailable"}</strong>
    <p>{result.message}</p>
    {result.observation && <dl>{fields.map(([label, value]) =>
      <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>}
  </div>;
}

function useLabelScan() {
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);

  async function scan(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || !consent || busy) return;
    setBusy(true);
    setResult(null);
    const form = new FormData();
    form.append("image", file);
    form.append("consent", "true");
    try {
      const response = await fetch(`${api}/api/v1/vision/label`, { method: "POST", body: form });
      if (!response.ok) throw new Error("Image reading unavailable");
      setResult(await response.json());
    } catch {
      setResult({ status: "offline", message: "Image reading is unavailable. Search by product name or type the label into a question.", observation: null });
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
          <p>Photograph the ingredients or warnings panel. Use the reading to check the names against the original label.</p>
          <form className="label-form" onSubmit={scan} aria-busy={busy}>
            <div className="label-upload">
              <label htmlFor="label-image">Package photo</label>
              <input id="label-image" type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => { setFile(event.target.files?.[0] || null); setResult(null); }} />
              <small>JPEG, PNG or WebP · up to 5 MB</small>
            </div>
            <label className="label-consent"><input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} /> Send this package photo to Gemini to read the text. Vivek does not retain the image.</label>
            <button className="primary-action" type="submit" disabled={!file || !consent || busy}>{busy ? "Reading…" : "Read label"} <span aria-hidden="true">↗</span></button>
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
