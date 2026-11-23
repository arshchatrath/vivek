"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import ConcernDictation from "../concern-dictation";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: ProductResult[];
  ingredients?: IngredientResult[];
  status?: string;
};

type ProductResult = {
  id: string;
  name: string;
  brand: string;
  price: number | null;
  currency: string | null;
  image_url: string | null;
  source_url: string;
  key_ingredients?: string[];
  nutritional_facts?: {
    serving_size?: string;
    nutrients?: { name: string; amount: number; unit: string; basis: string }[];
  };
};

type IngredientResult = {
  name: string;
  category: string;
  benefits: string[];
  evidence_level: string;
  source?: string;
};

type ChatReply = {
  response: string;
  products?: ProductResult[];
  ingredients?: IngredientResult[];
  status?: string;
};

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const CURRENCY_SYMBOLS: Record<string, string> = { INR: "₹", USD: "$" };

const suggestedQuestions = [
  "What products help with hair fall?",
  "How can I improve my sleep?",
  "What should I look for in a sunscreen?",
  "What vitamins are good for skin health?",
  "How to reduce acne and pimples?",
  "What is the serving size of Biotin Hair Gummies (30N)?",
];

async function requestReply(message: string, history: Message[], language: string): Promise<ChatReply> {
  const recent = history.slice(-4).map(({ role, content }) => ({ role, content: content.slice(0, 2000) }));
  const response = await fetch(API + "/api/v1/chat/general", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history: recent, language, share_with_groq: true }),
  });
  if (!response.ok) throw new Error("Chat failed");
  return response.json();
}

function ProductCard({ product }: { product: ProductResult }) {
  const { name, brand, price, currency, source_url, image_url, key_ingredients, nutritional_facts } = product;
  const currencyPrefix = currency ? (CURRENCY_SYMBOLS[currency] ?? currency + " ") : "";
  return (
    <a href={source_url} target="_blank" rel="noopener noreferrer" className="product-card-small">
      {image_url && <Image src={image_url} alt="" width={140} height={140} loading="lazy" />}
      <div className="product-card-info">
        <span className="product-card-brand">{brand}</span>
        <span className="product-card-name">{name}</span>
        {price != null && <span className="product-card-price">{currencyPrefix}{price}</span>}
        {key_ingredients?.length ? (
          <span className="product-card-ingredients">Listed ingredients: {key_ingredients.join(", ")}</span>
        ) : null}
        {nutritional_facts?.serving_size && (
          <span className="product-card-fact">Serving size: {nutritional_facts.serving_size}</span>
        )}
        {nutritional_facts?.nutrients?.map(({ name, amount, unit, basis }) => (
          <span key={name} className="product-card-fact">{name}: {amount} {unit} {basis}</span>
        ))}
      </div>
    </a>
  );
}

function IngredientNote({ ingredient }: { ingredient: IngredientResult }) {
  return (
    <div className="ingredient-chip">
      <span className="ingredient-name">{ingredient.name}</span>
      <span className="ingredient-benefit">{ingredient.benefits[0]}</span>
      <span className={"ingredient-evidence " + ingredient.evidence_level}>
        {ingredient.evidence_level.replace("_", " ")}
      </span>
      {ingredient.source && <span className="ingredient-reference">Reference: {ingredient.source}</span>}
    </div>
  );
}

function ChatTurn({ message }: { message: Message }) {
  const { role, content, products, ingredients, status } = message;
  const safety = status === "urgent" || status === "care_first";
  return (
    <article className={"message " + role} aria-label={role === "user" ? "You" : "Vivek"}>
      <div className={safety ? "message-content urgent-notice" : "message-content"}>
        {content.split("\n").map((line, i) => <p key={i}>{line || <br />}</p>)}
        {(status === "provider_unavailable" || status === "budget_limited") && (
          <Link href="/chat">Open sourced guides</Link>
        )}
      </div>
      {products?.length ? (
        <div className="message-products">
          <p className="products-label">Related brand listings</p>
          <div className="products-grid">
            {products.map((product) => <ProductCard key={product.id} product={product} />)}
          </div>
        </div>
      ) : null}
      {ingredients?.length ? (
        <div className="message-ingredients">
          <p className="ingredients-label">Ingredient notes</p>
          <div className="ingredients-list">
            {ingredients.map((ingredient) => <IngredientNote key={ingredient.name} ingredient={ingredient} />)}
          </div>
        </div>
      ) : null}
    </article>
  );
}

export default function GeneralChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("English");
  const scrollRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesRef = useRef<HTMLDivElement>(null);
  const nextMessageId = useRef(0);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const viewport = window.visualViewport;
    const element = scrollRef.current;
    if (!viewport || !element) return;
    const resize = () => {
      if (viewport.scale === 1) {
        element.style.setProperty("--chat-viewport-height", `${viewport.height}px`);
      }
    };
    resize();
    viewport.addEventListener("resize", resize);
    return () => viewport.removeEventListener("resize", resize);
  }, []);

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (text.length < 2 || loading) return;

    const userMessage: Message = { id: String(nextMessageId.current++), role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    let reply: ChatReply;
    try {
      reply = await requestReply(text, messages, language);
    } catch {
      reply = { response: "I'm having trouble connecting right now. Please try again in a moment." };
    }
    const { response, ...details } = reply;
    const answer: Message = { id: String(nextMessageId.current++), role: "assistant", content: response, ...details };
    setMessages((prev) => [...prev, answer]);
    setLoading(false);
  }

  function clearChat() {
    setMessages([]);
    setInput("");
    inputRef.current?.focus();
  }

  function selectSuggestion(question: string) {
    setInput(question);
    inputRef.current?.focus();
  }

  return (
    <main ref={scrollRef} className="general-chat" aria-label="General wellness chat">
      <header className="chat-header">
        <Link href="/" className="brand-lockup" aria-label="Vivek home">
          <span className="brand-symbol" aria-hidden="true">✳</span>vivek<span className="brand-period">.</span>
        </Link>
        <div className="chat-header-actions">
          <label className="chat-language">
            Language
            <select value={language} onChange={(e) => setLanguage(e.target.value)} className="language-select">
              <option value="English">English</option>
              <option value="Hindi">हिंदी</option>
              <option value="Hinglish">Hinglish</option>
            </select>
          </label>
          <Link href="/chat" className="nav-link">Sourced guides</Link>
          <button
            className="clear-button"
            type="button"
            disabled={loading || messages.length === 0}
            onClick={clearChat}
          >
            New chat
          </button>
        </div>
      </header>

      <div ref={messagesRef} className="chat-messages" tabIndex={0} aria-label="Conversation">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <h1>General <em>wellness chat</em></h1>
            <p>
              I can help with hair care, skin care, nutrition, sleep, and general wellness.
              I also know about products from Man Matters, Be Bodywise, Little Joys, and Root Labs.
            </p>
            <div className="suggestions-grid">
              {suggestedQuestions.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="suggestion-button"
                  onClick={() => selectSuggestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages-list" role="log" aria-label="Chat messages">
            {messages.map((message) => <ChatTurn key={message.id} message={message} />)}
            {loading && (
              <article className="message assistant loading">
                <div className="message-content">
                  <p>Thinking...</p>
                </div>
              </article>
            )}
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <form className="chat-form" onSubmit={sendMessage} aria-busy={loading}>
          <label htmlFor="wellness-question" className="chat-field-label">Wellness question</label>
          <textarea
            id="wellness-question"
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about wellness, products, ingredients..."
            aria-describedby="chat-sharing"
            rows={2}
            maxLength={1500}
            required
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <div className="chat-actions">
            <ConcernDictation
              disabled={loading}
              onTranscript={(text) => {
                setInput((prev) => `${prev.trimEnd()} ${text}`.trimStart().slice(0, 1500));
              }}
            />
            <button
              className="send-button"
              type="submit"
              disabled={loading || input.trim().length < 2}
            >
              {loading ? "Sending…" : "Send to Groq"} <span aria-hidden="true">↑</span>
            </button>
          </div>
        </form>
        <p className="chat-disclaimer" id="chat-sharing">
          Sending shares your question and up to four recent messages with Groq. <Link href="/chat">Use sourced guides for health concerns.</Link>
        </p>
      </div>
    </main>
  );
}
