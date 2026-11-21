"use client";

import { useId, useRef, useState, type FormEvent } from "react";
import ConcernDictation from "./concern-dictation";
import SuggestedProducts, { type ListingSummary, type ProductSuggestion } from "./suggested-products";

type Topic = { id: string; title: string };
type Source = { title: string; publisher: string; url: string };
type Passage = { id: string; title: string; text: string; source: Source };
type Ingredient = { name: string; form: string; evidence: Source; products: ListingSummary[] };
export type ConcernResponse = {
  status: "guidance" | "care_first" | "urgent" | "clarify" | "outside_coverage";
  message?: string;
  topic?: Topic;
  topics?: Topic[];
  guidance?: Passage[];
  followup?: Passage[];
  ingredients?: Ingredient[];
  can_retry_with_groq?: boolean;
};

type ConcernOptions = { topic?: string; shareFollowup?: boolean; shareRouting?: boolean };

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const concernLimit = 1000;

const examples = [
  ["Scalp flakes", "My scalp is itchy and has white flakes."],
  ["Acne", "I keep getting pimples and blackheads."],
  ["Hair thinning", "My hair has been thinning over several months."],
  ["Dry skin", "My skin feels dry and tight after washing."],
  ["Rough bumps", "I have rough bumps on my arms."],
  ["Sun protection", "What should I look for in a sunscreen?"],
  ["Dry hair", "My hair feels dry and frizzy."],
  ["Body odor", "What can help with body odor?"],
  ["Sleep", "I've been having trouble sleeping."],
  ["Cavity prevention", "What should I look for in toothpaste to prevent cavities?"],
  ["Dark spots", "I notice dark spots on my face."],
  ["Constipation", "I have been constipated lately."],
];

export async function fetchConcern(concern: string, { topic, shareFollowup, shareRouting }: ConcernOptions = {}): Promise<ConcernResponse> {
  const response = await fetch(`${API}/api/v1/concerns`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ concern, topic, share_followup: shareFollowup, share_routing: shareRouting }),
  });
  if (!response.ok) throw new Error("Guidance request failed");
  return response.json();
}

export function Examples({ pending, select }: { pending: boolean; select: (example: string) => void }) {
  const renderExample = ([label, text]: string[]) => (
    <button key={label} type="button" disabled={pending} onClick={() => select(text)}>{label}</button>
  );
  return <details className="example-list">
    <summary>Try an example</summary>
    <div className="concern-examples">{examples.map(renderExample)}</div>
  </details>;
}

function EvidenceCards({ cards }: { cards: Passage[] }) {
  return <div className="concern-cards">
    {cards.map((card) => <article className="evidence-card" key={card.id}>
      <h4>{card.title}</h4>
      <p>{card.text}</p>
      <a href={card.source.url} target="_blank" rel="noopener noreferrer">{card.source.publisher} ↗</a>
    </article>)}
  </div>;
}

function ConcernProducts({ ingredients }: { ingredients: Ingredient[] }) {
  const suggestions = new Map<string, ProductSuggestion>();
  for (const { name, form, evidence, products } of ingredients) {
    for (const listing of products) {
      const reasons = suggestions.get(listing.id)?.reasons ?? [];
      suggestions.set(listing.id, { listing, reasons: [...reasons, { name, form, evidence }] });
    }
  }
  return <SuggestedProducts products={[...suggestions.values()]}
    note="These listings name an ingredient or product type discussed in the guide. Check the current label for ingredients and warnings." />;
}

function UnmatchedIngredients({ ingredients }: { ingredients: Ingredient[] }) {
  const unmatched = ingredients.filter(({ products }) => !products.length);
  if (!unmatched.length) return null;
  return <details className="example-list ingredient-guidance">
    <summary>Ingredient guidance without a catalog match</summary>
    <div className="concern-cards">
      {unmatched.map((ingredient) => <article className="evidence-card" key={ingredient.name}>
        <h4>{ingredient.name}</h4>
        <p>{ingredient.form}</p>
        <a href={ingredient.evidence.url} target="_blank" rel="noopener noreferrer">{ingredient.evidence.title} ↗</a>
      </article>)}
    </div>
  </details>;
}

export function FollowupInfo({ id }: { id: string }) {
  return <details className="followup-info">
    <summary aria-label="About follow-up questions"><span aria-hidden="true">i</span></summary>
    <p id={id}>Sending a follow-up shares your question and the selected guidance passages with Groq. Leave out names and contact details.</p>
  </details>;
}

function SourcedAnswer({ result }: { result: ConcernResponse }) {
  return <>
    {result.followup?.length ? <div className="concern-followup">
      <h3>Relevant passages for your question</h3><EvidenceCards cards={result.followup} />
    </div> : null}
    {result.status === "guidance" && <ConcernProducts ingredients={result.ingredients ?? []} />}
    {result.guidance?.length ? <EvidenceCards cards={result.guidance} /> : null}
    {result.ingredients?.length ? <UnmatchedIngredients ingredients={result.ingredients} /> : null}
  </>;
}

export function ConcernResult({ result, chooseTopic, tryGroq, pending = false }: {
  result: ConcernResponse;
  chooseTopic: (topic: string) => void;
  tryGroq?: () => void;
  pending?: boolean;
}) {
  const routingNote = useId();

  return <>
    <h3>{result.status === "urgent" ? "Seek urgent help" : result.topic?.title || "Find relevant guidance"}</h3>
    {result.message && <p className="concern-message">{result.message}</p>}
    {result.can_retry_with_groq && tryGroq && <div className="concern-routing">
      <button type="button" className="concern-reset" disabled={pending} onClick={tryGroq} aria-describedby={routingNote}>Try with Groq</button>
      <p id={routingNote}>This sends your question to Groq to find a guide. Leave out names and contact details.</p>
    </div>}
    {result.topics && <div className="concern-examples">
      {result.topics.map((topic) => <button type="button" key={topic.id} disabled={pending} onClick={() => chooseTopic(topic.id)}>{topic.title}</button>)}
    </div>}
    <SourcedAnswer result={result} />
  </>;
}

function useConcernGuide() {
  const [concern, setConcern] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [result, setResult] = useState<ConcernResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [followup, setFollowup] = useState<Topic | null>(null);
  const field = useRef<HTMLTextAreaElement>(null);
  const output = useRef<HTMLDivElement>(null);

  async function requestGuidance(options: ConcernOptions = {}, text = concern) {
    if (pending) return;
    const question = text.trim();
    if (question.length < 3) {
      setError("Enter a few words about what you’re experiencing.");
      field.current?.focus();
      return;
    }
    setPending(true);
    setSubmitted(question);
    setError("");
    if (!options.shareRouting) setResult(null);
    try {
      setResult(await fetchConcern(question, options));
      requestAnimationFrame(() => output.current?.focus());
    } catch {
      setError("Vivek couldn’t load guidance. Try again in a moment.");
    } finally {
      setPending(false);
    }
  }

  function selectExample(example: string) {
    setFollowup(null);
    setConcern(example);
    setResult(null);
    setError("");
    field.current?.focus();
  }

  function askFollowup(topic: Topic) {
    setFollowup(topic);
    setConcern("");
    field.current?.focus();
  }

  return { concern, setConcern, submitted, result, pending, error, followup,
    field, output, selectExample, askFollowup, requestGuidance };
}

function ConcernForm({ guide }: { guide: ReturnType<typeof useConcernGuide> }) {
  const { concern, setConcern, pending, error, followup, field, selectExample, requestGuidance } = guide;
  const [inputLabel, placeholder, submitLabel] = followup
    ? [`Follow-up about ${followup.title.toLowerCase()}`, "For example: When should I get it checked?", "Ask with Groq"]
    : ["What are you experiencing?", "For example: My scalp is itchy and has white flakes.", "Find guidance"];

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void requestGuidance({ topic: followup?.id, shareFollowup: Boolean(followup) });
  }

  return <form className="concern-form app-frame" onSubmit={submit} aria-busy={pending}>
    <label htmlFor="concern-input">{inputLabel}</label>
    <textarea ref={field} id="concern-input" value={concern} onChange={(event) => setConcern(event.target.value)}
      rows={3} maxLength={concernLimit} required placeholder={placeholder} aria-describedby="concern-input-help" />
    <div className="concern-field-tools">
      <small id="concern-input-help">Include how long it’s lasted. Leave out names and contact details.
        <span id="concern-mic-help">Voice clips go to Gnani for transcription.</span>
      </small>
      <ConcernDictation disabled={pending} onTranscript={(text) => {
        setConcern((previous) => `${previous.trimEnd()} ${text}`.trimStart().slice(0, concernLimit));
      }} />
    </div>
    <div className="concern-form-actions">
      <button className="primary-action" type="submit" disabled={pending} aria-describedby={followup ? "home-followup-help" : undefined}>
        {pending ? "Finding guidance…" : submitLabel}<span aria-hidden="true">↗</span>
      </button>
      {followup && <FollowupInfo id="home-followup-help" />}
      {followup && <button className="concern-reset" type="button" disabled={pending} onClick={() => selectExample("")}>Start a new concern</button>}
    </div>
    {!followup && <Examples pending={pending} select={selectExample} />}
    {error && <p role="alert">{error}</p>}
  </form>;
}

export default function ConcernGuide({ catalogSize }: { catalogSize: number }) {
  const guide = useConcernGuide();
  const { result, concern, submitted, output, askFollowup, requestGuidance } = guide;
  const followupTopic = result?.status === "guidance" ? result.topic : undefined;
  return <>
    <section id="concern" className="hero concern-section" data-enter aria-labelledby="concern-title">
      <div className="wrap">
        <div className="hero-text concern-layout">
          <div className="concern-intro">
            <h1 id="concern-title">Guidance for <em>your concern.</em></h1>
            <p className="hero__lead">Read guidance from health organizations, check the original sources, and find products that list relevant ingredients.</p>
            <div className="guide-scope">
              <span><strong>{examples.length}</strong> health guides</span>
              <a href="#catalog"><strong>{catalogSize}</strong> product listings <span aria-hidden="true">↗</span></a>
            </div>
          </div>
          <ConcernForm guide={guide} />
        </div>
      </div>
    </section>
    <section id="guidance" aria-label="Concern results" hidden={!result}>
      <div className="wrap">
        <div className={result ? `concern-output ${result.status}` : undefined} tabIndex={-1} ref={output} aria-live="polite">
          {result && <ConcernResult result={result} pending={guide.pending}
            chooseTopic={(topic) => void requestGuidance({ topic }, submitted)}
            tryGroq={concern.trim() === submitted ? () => void requestGuidance({ shareRouting: true }, submitted) : undefined} />}
          {followupTopic && <button className="concern-reset" type="button" onClick={() => askFollowup(followupTopic)}>Ask a follow-up ↗</button>}
        </div>
      </div>
    </section>
  </>;
}
