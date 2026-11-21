"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import ConcernDictation from "../concern-dictation";
import { ConcernResult, Examples, FollowupInfo, concernLimit, fetchConcern, type ConcernResponse } from "../concern-guide";

type Turn = {
  question: string;
  topic?: string;
  followup: boolean;
  result?: ConcernResponse;
  failed?: boolean;
};

export default function Conversation() {
  const [draft, setDraft] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [pending, setPending] = useState<number | null>(null);
  const workspace = useRef<HTMLElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const lastTurn = useRef<HTMLLIElement>(null);
  const latest = [...turns].reverse().find((turn) => turn.result)?.result;
  const topic = latest?.status === "guidance" ? latest.topic : undefined;

  useEffect(() => {
    lastTurn.current?.scrollIntoView({ block: "start", inline: "nearest" });
  }, [turns.length]);

  useEffect(() => {
    const viewport = window.visualViewport;
    const element = workspace.current;
    if (!viewport || !element) return;
    const resize = () => {
      if (viewport.scale === 1) element.style.setProperty("--chat-viewport-height", `${viewport.height}px`);
    };
    resize();
    viewport.addEventListener("resize", resize);
    return () => viewport.removeEventListener("resize", resize);
  }, []);

  async function ask(turn: Turn, index: number) {
    if (pending !== null) return;
    setPending(index);
    setTurns((previous) => index === previous.length ? [...previous, turn] : previous.map((item, position) => position === index ? turn : item));
    try {
      const result = await fetchConcern(turn.question, turn.topic, turn.followup);
      setTurns((previous) => previous.map((item, position) => position === index ? { ...turn, result } : item));
    } catch {
      setTurns((previous) => previous.map((item, position) => position === index ? { ...turn, failed: true } : item));
    } finally {
      setPending(null);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const question = draft.trim();
    if (question.length < 3 || pending !== null) return;
    const turn = { question, topic: topic?.id, followup: Boolean(topic) };
    setDraft("");
    void ask(turn, turns.length);
  }

  function newChat() {
    setTurns([]);
    setDraft("");
    input.current?.focus();
  }

  return <main ref={workspace} className="conversation" aria-labelledby="conversation-title">
    <header className="conversation-header">
      <Link href="/" className="brand-lockup" aria-label="Vivek home">
        <span className="brand-symbol" aria-hidden="true">✳</span>vivek<span className="brand-period">.</span>
      </Link>
      <div className="conversation-links">
        <Link href="/#assistant">Product questions</Link>
        <button className="concern-reset" type="button" disabled={pending !== null || (!turns.length && !draft)} onClick={newChat}>New chat</button>
      </div>
    </header>

    <div className="conversation-scroll" tabIndex={0} aria-label="Conversation">
      {!turns.length ? <section className="conversation-welcome">
        <h1 id="conversation-title">What’s on <em>your mind?</em></h1>
        <p>Describe a wellness concern. Vivek will find guidance, show its sources, and link to product examples where available.</p>
        <Examples pending={false} select={(example) => {
          setDraft(example);
          input.current?.focus();
        }} />
      </section> : <>
        <h1 id="conversation-title" className="conversation-sr-only">Vivek chat</h1>
        <ol className="conversation-thread" aria-label="Messages">
          {turns.map((turn, index) => <li key={index} ref={index === turns.length - 1 ? lastTurn : undefined} className="conversation-turn">
            <p className="conversation-question"><span className="conversation-sr-only">You: </span>{turn.question}</p>
            <div className="conversation-reply" aria-live="polite">
              {pending === index && <p className="conversation-pending">Finding relevant guidance…</p>}
              {turn.failed && <div className="conversation-error">
                <p>Vivek couldn’t load guidance.</p>
                <button className="concern-reset" type="button" disabled={pending !== null} onClick={() => void ask({ ...turn, failed: false }, index)}>Try again</button>
              </div>}
              {turn.result && <article aria-label="Vivek’s answer" className={`concern-output ${turn.result.status}`}>
                <ConcernResult result={turn.result} pending={pending !== null}
                  chooseTopic={(selected) => void ask({ question: turn.question, topic: selected, followup: false }, index)} />
              </article>}
            </div>
          </li>)}
        </ol>
      </>}
    </div>

    <div className="conversation-dock">
      <form className="conversation-composer" onSubmit={submit} aria-busy={pending !== null}>
        <label className="conversation-sr-only" htmlFor="chat-question">Your question</label>
        <textarea id="chat-question" ref={input} value={draft} onChange={(event) => setDraft(event.target.value)}
          required minLength={3} maxLength={concernLimit} rows={2}
          placeholder={topic ? "Ask a follow-up…" : "Describe your concern…"}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }} />
        <div className="conversation-actions">
          <div className="conversation-voice">
            <ConcernDictation disabled={pending !== null} onTranscript={(text) => {
              setDraft((previous) => `${previous.trimEnd()} ${text}`.trimStart().slice(0, concernLimit));
            }} />
          </div>
          {topic && <FollowupInfo id="chat-followup-help" />}
          <button className="primary-action" type="submit" disabled={pending !== null || draft.trim().length < 3} aria-describedby={topic ? "chat-followup-help" : undefined}>
            {topic ? "Ask with Groq" : "Send"} <span aria-hidden="true">↑</span>
          </button>
        </div>
      </form>
      <p className="conversation-note">Leave out names and contact details. <span id="concern-mic-help">Voice clips go to Gnani for transcription.</span></p>
    </div>
  </main>;
}
