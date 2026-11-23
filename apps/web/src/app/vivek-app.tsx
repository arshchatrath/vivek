"use client";

import { type FormEvent, type ReactNode, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import LabelScanner from "./label-scanner";
import ConcernGuide from "./concern-guide";
import OpeningScreen from "./opening-screen";
import ProductMotion from "./product-motion";
import { displayPrice, formatCaptureDate, usdReference } from "./catalog-display";
import SuggestedProducts, { type ListingSummary } from "./suggested-products";

type Product = { id: string; brand: string; region: string; name: string; description: string | null; category: string | null; image_url: string | null; price: number | null; currency: string | null; ingredients: string[] | null; warnings: string[] | null; age_restrictions: string | null; source_url: string; captured_at: string };
type Source = Pick<ListingSummary, "id" | "captured_at" | "image_url" | "price" | "currency" | "availability"> & {
  title: string;
  url: string;
  publisher: string;
};
type Answer = { answer: string; sources: Source[]; status: string; provider: string | null };
const brands = ["All brands", "Man Matters", "Be Bodywise", "Little Joys", "Root Labs"];
const productsPerPage = 8;
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const dollars = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function ExchangeRateNote() {
  return <p>USD prices are estimated in rupees using the <a href={usdReference.url} target="_blank" rel="noopener noreferrer">FBIL reference rate for {usdReference.date}</a>. Checkout prices may differ.</p>;
}

function useVivekState(products: Product[], coverage: Record<string, { discovered?: number }>) {
  const [selected, setSelected] = useState<string[]>([]);
  const [detail, setDetail] = useState<Product | null>(null);
  const [compareOpen, setCompareOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [language, setLanguage] = useState("English");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [asking, setAsking] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const compared = products.filter((product) => selected.includes(product.id));
  const discovered = Object.values(coverage).reduce((n, item) => n + (item.discovered || 0), 0);
  const toggle = (product: Product) => setSelected((current) => current.includes(product.id) ? current.filter((id) => id !== product.id) : current.length < 4 ? [...current, product.id] : current);

  async function ask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!question.trim() || asking) return;
    setSubmittedQuestion(question.trim());
    setAsking(true); setAnswer(null);
    try {
      const response = await fetch(`${api}/api/v1/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question, product_ids: selected, language }) });
      if (!response.ok) throw new Error("API unavailable");
      setAnswer(await response.json());
    } catch {
      setAnswer({
        answer: "The text assistant is offline. You can still inspect and compare official product listings.",
        sources: compared.map(({ id, name, source_url, captured_at, brand, image_url, price, currency }) => ({
          id, title: name, url: source_url, captured_at, publisher: brand, image_url, price, currency,
        })),
        status: "offline",
        provider: null,
      });
    } finally { setAsking(false); }
  }

  return { selected, setSelected, detail, setDetail, compareOpen, setCompareOpen, question, submittedQuestion, setQuestion, language, setLanguage, answer, asking, menuOpen, setMenuOpen, compared, discovered, toggle, ask };
}

const mainLinks = [
  ["#concern", "Find guidance"],
  ["#catalog", "Products"],
  ["#assistant", "Product questions"],
  ["#label", "Read a label"],
  ["#method", "Sources"],
];

function Navigation({ menuOpen, setMenuOpen }: { menuOpen: boolean; setMenuOpen: (open: boolean) => void }) {
  return (
    <header className="nav site-nav">
      <div className="wrap nav-inner">
        <a className="skip-link" href="#main">Skip to content</a>
        <a className="brand-lockup" href="#top" aria-label="Vivek home">
          <span className="brand-symbol" aria-hidden="true">✳</span>vivek<span className="brand-period">.</span>
        </a>
        <nav className={menuOpen ? "nav-links open" : "nav-links"} id="main-navigation" aria-label="Main">
          {mainLinks.map(([href, label]) => <a key={href} href={href} onClick={() => setMenuOpen(false)}>{label}</a>)}
        </nav>
        <div className="nav-actions">
          <Link className="nav-chat-link" href="/chat">Open chat <span aria-hidden="true">↗</span></Link>
          <button className="menu-toggle" type="button" aria-label={menuOpen ? "Close navigation" : "Open navigation"} aria-controls="main-navigation" aria-expanded={menuOpen} onClick={() => setMenuOpen(!menuOpen)}>
            <span aria-hidden="true">{menuOpen ? "×" : "☰"}</span>
          </button>
        </div>
      </div>
      <OpeningScreen />
    </header>
  );
}

function SourceNotes({ count, discovered, generatedAt, example }: { count: number; discovered: number; generatedAt: string; example?: Product }) {
  return (
    <footer id="method" className="closing site-footer" aria-labelledby="method-title">
      <div className="wrap">
        <div className="closing__cta">
          <h2 id="method-title">Check the original source.</h2>
          <div className="source-layout">
            <div>
              <p>Health guides link to their publishers, and product records link to the original brand listings. Ingredients and warnings stay marked as unknown until they can be verified.</p>
              <a className="primary-action" href="#concern">Find guidance <span aria-hidden="true">↗</span></a>
            </div>
            <div className="source-visual">
              {example?.image_url && <a className="source-visual-link" href={example.source_url} target="_blank" rel="noopener noreferrer" aria-label={`View original ${example.name} listing`}>
                <img src={example.image_url} alt={example.name} width="600" height="600" loading="lazy" />
                <span>{example.brand} listing ↗</span>
              </a>}
              <dl className="source-register" data-moment="counter-rolls">
                <div><dt>Catalog records</dt><dd><span data-count>{count}</span> listings</dd></div>
                <div><dt>Official sitemap URLs</dt><dd><span data-count>{discovered}</span></dd></div>
                <div><dt>Catalog snapshot</dt><dd>{formatCaptureDate(generatedAt)}</dd></div>
              </dl>
            </div>
          </div>
        </div>
        <div className="closing__links footer-layout">
          <a href="#top" className="footer-brand" aria-label="Vivek home">vivek.</a>
          <p>Built for the Mosaic Fellowship. <Link href="/chat/general">Open general wellness chat</Link>.</p>
        </div>
      </div>
    </footer>
  );
}

function CompareBar({ count, clear, open }: { count: number; clear: () => void; open: () => void }) {
  return <div className="compare-bar">
    <div className="compare-bar-inner">
      <div><strong role="status">{count} selected</strong><span>Choose 2–4 products</span></div>
      <div>
        <button type="button" onClick={clear}>Clear</button>
        <button className="primary-action" type="button" disabled={count < 2} onClick={open}>Compare products <span aria-hidden="true">↗</span></button>
      </div>
    </div>
  </div>;
}

export default function VivekApp({ products, generatedAt, coverage }: { products: Product[]; generatedAt: string; coverage: Record<string, { discovered?: number }> }) {
  const { selected, setSelected, detail, setDetail, compareOpen, setCompareOpen, question, submittedQuestion, setQuestion, language, setLanguage, answer, asking, menuOpen, setMenuOpen, compared, discovered, toggle, ask } = useVivekState(products, coverage);
  const labelImage = products.find((product) => product.name === "Nutrimix Vanilla Nutrition Powder (350g)")?.image_url;
  const questionExample = products.find((product) => product.name === "1% Ketoconazole Dandruff Shampoo");
  const sourceExample = products.find((product) => product.name === "REJUV Niacinamide Serum");

  return <>
    <ProductMotion />
    <Navigation menuOpen={menuOpen} setMenuOpen={setMenuOpen} />
    <main id="main">
      <ConcernGuide catalogSize={products.length} />
      <Catalog products={products} selected={selected} toggle={toggle} setDetail={setDetail} comparison={<>
        {selected.length > 0 && <CompareBar count={selected.length} clear={() => setSelected([])} open={() => setCompareOpen(true)} />}
        <ProductDetail detail={detail} setDetail={setDetail} />
        <ComparisonDialog compareOpen={compareOpen} setCompareOpen={setCompareOpen} compared={compared} />
      </>} />
      <AssistantPanel selected={selected} answer={answer} question={question} submittedQuestion={submittedQuestion} setQuestion={setQuestion} language={language} setLanguage={setLanguage} asking={asking} ask={ask} example={questionExample} />
      <LabelScanner imageUrl={labelImage} />
    </main>
    <SourceNotes count={products.length} discovered={discovered} generatedAt={generatedAt} example={sourceExample} />
  </>;
}

type CatalogActions = {
  toggle: (product: Product) => void;
  setDetail: (product: Product) => void;
};

function ProductPhoto({ product, detail = false }: { product: Product; detail?: boolean }) {
  return <span className={detail ? "detail-photo" : "product-photo"}>
    <span className="product-photo-fallback" aria-hidden="true">{product.brand}</span>
    {product.image_url && <img src={product.image_url} alt="" loading={detail ? "eager" : "lazy"}
      onError={(event) => { event.currentTarget.hidden = true; }} />}
  </span>;
}

function ProductCard({ product, selected, atLimit, toggle, setDetail }: CatalogActions & {
  product: Product;
  selected: boolean;
  atLimit: boolean;
}) {
  return (
    <article className="product-card">
      <button className="product-open" type="button" onClick={() => setDetail(product)} aria-label={`Open ${product.name} details`}>
        <ProductPhoto product={product} />
        <span className="product-body">
          <span className="product-brand">{product.brand} · {product.region}</span>
          <strong className="product-name">{product.name} <span className="listing-arrow" aria-hidden="true">↗</span></strong>
          <span className="listing-meta">
            <span className="product-price">{displayPrice(product)}</span>
            <span className="source-mark">Official listing · {formatCaptureDate(product.captured_at)}</span>
          </span>
        </span>
      </button>
      <button
        className={selected ? "compare-add selected" : "compare-add"}
        type="button"
        aria-label={selected ? "Added to compare" : "Add to compare"}
        aria-pressed={selected}
        disabled={atLimit && !selected}
        onClick={() => toggle(product)}
      >
        <span aria-hidden="true">{selected ? "✓" : "+"}</span> Compare
      </button>
    </article>
  );
}

function interleaveBrands(products: Product[]) {
  const groups = new Map<string, Product[]>();
  for (const product of products) {
    const group = groups.get(product.brand);
    if (group) group.push(product);
    else groups.set(product.brand, [product]);
  }
  const ordered: Product[] = [];
  const longest = Math.max(0, ...Array.from(groups.values(), (group) => group.length));
  for (let index = 0; index < longest; index++) {
    for (const group of groups.values()) {
      if (group[index]) ordered.push(group[index]);
    }
  }
  return ordered;
}

function filterCatalog(products: Product[], query: string, brand: string) {
  const words = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  if (!words.length && brand === "All brands") return interleaveBrands(products);
  const matches = products.filter((product) => {
    if (brand !== "All brands" && product.brand !== brand) return false;
    const text = [product.name, product.brand, product.category, product.description, ...(product.ingredients ?? [])]
      .join(" ").toLocaleLowerCase();
    return words.every((word) => text.includes(word));
  });
  if (!words.length) return matches;
  const phrase = words.join(" ");
  const titleScore = (product: Product) => {
    const name = product.name.toLocaleLowerCase();
    if (name === phrase) return 2;
    return words.every((word) => name.includes(word)) ? 1 : 0;
  };
  return matches.sort((first, second) => titleScore(second) - titleScore(first));
}

function CatalogControls({ query, brand, onQuery, onBrand }: {
  query: string;
  brand: string;
  onQuery: (value: string) => void;
  onBrand: (value: string) => void;
}) {
  return (
    <div className="catalog-controls">
      <div className="catalog-search">
        <label htmlFor="catalog-search">Search products</label>
        <input id="catalog-search" type="search" value={query} onChange={(event) => onQuery(event.target.value)} placeholder="Try a product name or category" />
      </div>
      <div className="catalog-brand-picker">
        <label htmlFor="catalog-brand">Filter by brand</label>
        <select id="catalog-brand" value={brand} onChange={(event) => onBrand(event.target.value)}>
          {brands.map((item) => <option key={item}>{item}</option>)}
        </select>
      </div>
      <div className="brand-tabs" role="group" aria-label="Filter by brand">
        {brands.map((item) => (
          <button type="button" className={brand === item ? "brand-tab active" : "brand-tab"} aria-pressed={brand === item} key={item} onClick={() => onBrand(item)}>
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

function CatalogPagination({ page, last, goToPage }: { page: number; last: boolean; goToPage: (next: number) => void }) {
  return <nav className="catalog-pagination" aria-label="Product results pages">
    <button type="button" className="brand-tab" disabled={!page} onClick={() => goToPage(page - 1)}>Previous page</button>
    <button type="button" className="brand-tab" disabled={last} onClick={() => goToPage(page + 1)}>Next page</button>
  </nav>;
}

function CatalogGrid({ products, selected, toggle, setDetail }: CatalogActions & {
  products: Product[];
  selected: string[];
}) {
  const renderProduct = (product: Product) => (
    <ProductCard key={product.id} product={product} selected={selected.includes(product.id)}
      atLimit={selected.length >= 4} setDetail={setDetail} toggle={toggle} />
  );
  return <>
    {products.length > 0 && <div className="product-shelf">{products.slice(0, 4).map(renderProduct)}</div>}
    {products.length > 4 && <div className="product-ledger">{products.slice(4).map(renderProduct)}</div>}
  </>;
}

function Catalog({ products, selected, toggle, setDetail, comparison }: CatalogActions & {
  products: Product[];
  selected: string[];
  comparison?: ReactNode;
}) {
  const [query, setQuery] = useState("");
  const [brand, setBrand] = useState("All brands");
  const [page, setPage] = useState(0);
  const results = useRef<HTMLParagraphElement>(null);
  const filtered = useMemo(() => filterCatalog(products, query, brand), [products, query, brand]);
  const start = page * productsPerPage;
  const end = Math.min(start + productsPerPage, filtered.length);
  const pageProducts = filtered.slice(start, end);

  function goToPage(next: number) {
    setPage(next);
    results.current?.focus();
  }

  return (
    <section id="catalog" className="catalog-section" aria-labelledby="catalog-title">
      <div className="wrap">
        <h2 id="catalog-title">Product catalog.</h2>
        <p className="catalog-intro">Compare prices and details from the original brand listings.</p>
        <CatalogControls
          query={query}
          brand={brand}
          onQuery={(value) => { setQuery(value); setPage(0); }}
          onBrand={(value) => { setBrand(value); setPage(0); }}
        />
        <p className="catalog-results" ref={results} tabIndex={-1} role="status">
          {filtered.length ? `Products ${start + 1}–${end} of ${filtered.length}` : "No matching products"}
        </p>
        <CatalogGrid products={pageProducts} selected={selected} setDetail={setDetail} toggle={toggle} />
        {!filtered.length && <div className="empty-state">
          <p>Try another product name or clear your filters.</p>
          <button className="brand-tab" type="button" onClick={() => {
            setQuery("");
            setBrand("All brands");
            setPage(0);
            document.getElementById("catalog-search")?.focus();
          }}>Clear filters</button>
        </div>}
        {filtered.length > productsPerPage && <CatalogPagination page={page} last={end === filtered.length} goToPage={goToPage} />}
        {comparison}
      </div>
    </section>
  );
}


type AssistantProps = {
  selected: string[];
  answer: Answer | null;
  question: string;
  submittedQuestion: string;
  setQuestion: (value: string) => void;
  language: string;
  setLanguage: (value: string) => void;
  asking: boolean;
  ask: (event: FormEvent<HTMLFormElement>) => void;
  example?: Product;
};

function ProductAnswer({ answer, question }: { answer: Answer; question: string }) {
  const suggestions = answer.sources.map(({ title, publisher, url, ...listing }, index) => ({
    listing: { ...listing, name: title, brand: publisher, source_url: url },
    citation: answer.status === "grounded" ? index + 1 : undefined,
  }));
  return <div className="chat-answer">
    <p className="chat-user">{question}</p>
    <p className="answer-text">{answer.answer}</p>
    {suggestions.length > 0 && <SuggestedProducts products={suggestions} title="Products in this answer" />}
  </div>;
}

function SampleProductQuestion({ example, setQuestion }: { example?: Product; setQuestion: (value: string) => void }) {
  if (!example) return null;
  const sample = `What price and warnings are listed for ${example.brand} ${example.name}?`;
  return <button className="text-action" type="button" onClick={() => setQuestion(sample)}>Try a sample question ↗</button>;
}

function AssistantPanel({ selected, answer, question, submittedQuestion, setQuestion, language, setLanguage, asking, ask, example }: AssistantProps) {
  return <section id="assistant" className="tool-section" aria-labelledby="assistant-title">
    <div className="wrap">
      <h2 id="assistant-title">Ask about a product.</h2>
      <div className="tool-split">
        <div className="tool-copy">
          <p>Use a product name or select listings in the catalog to ask about prices, ingredients, or warnings.</p>
          <form className="chat-form" onSubmit={ask} aria-busy={asking}>
            <label htmlFor="question">Your product question</label>
            <div className="chat-entry">
              <input id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What does the product listing say?" maxLength={1200} />
              <button className="primary-action" type="submit" disabled={asking || question.trim().length < 3} aria-label="Send product question">
                {asking ? "Sending…" : "Ask"} <span aria-hidden="true">↗</span>
              </button>
            </div>
            <div className="chat-options">
              <label>Answer language
                <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                  <option>English</option><option>Hindi</option><option>Hinglish</option>
                </select>
              </label>
              <span>{selected.length ? `${selected.length} selected` : "Catalog sources"}</span>
            </div>
            {!answer && !asking && <SampleProductQuestion example={example} setQuestion={setQuestion} />}
          </form>
          <div aria-live="polite">
            {asking && <p className="pending-answer">Checking catalog sources…</p>}
            {answer && <ProductAnswer answer={answer} question={submittedQuestion} />}
          </div>
        </div>
        {example?.image_url && <figure className="tool-visual question-visual">
          <img src={example.image_url} alt={example.name} width="600" height="600" loading="lazy" />
          <a href={example.source_url} target="_blank" rel="noopener noreferrer">{example.brand} listing ↗</a>
        </figure>}
      </div>
    </div>
  </section>;
}

function Dialog({ kind, title, onDismiss, children }: {
  kind: "detail" | "comparison";
  title: string;
  onDismiss: () => void;
  children: ReactNode;
}) {
  const element = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = element.current;
    if (dialog && !dialog.open) dialog.showModal();
  }, []);
  return (
    <dialog
      ref={element}
      className={`${kind}-modal`}
      aria-labelledby={title}
      onClose={onDismiss}
      onClick={(event) => {
        if (event.target === event.currentTarget) event.currentTarget.close();
      }}
    >
      <div className="dialog-content">
        <button className="modal-close" type="button" onClick={() => element.current?.close()} aria-label="Close dialog">×</button>
        {children}
      </div>
    </dialog>
  );
}

function verifiedList(values: string[] | null) {
  return values?.join(", ") || "Not yet verified";
}

function ProductDetail({ detail, setDetail }: { detail: Product | null; setDetail: (product: Product | null) => void }) {
  if (!detail) return null;
  const originalPrice = detail.currency === "USD" && typeof detail.price === "number" ? dollars.format(detail.price) : null;
  return (
    <Dialog kind="detail" title="detail-title" onDismiss={() => setDetail(null)}>
      <ProductPhoto product={detail} detail />
      <div className="detail-info">
        <span className="product-brand">{detail.brand} · {detail.region}</span>
        <h2 id="detail-title">{detail.name}</h2>
        <p>{detail.description || "No manufacturer description recorded."}</p>
        <small>Manufacturer description</small>
        <dl>
          <div><dt>Price at capture (₹)</dt><dd>{displayPrice(detail)}</dd></div>
          {originalPrice && <div><dt>Original US price</dt><dd>{originalPrice} USD</dd></div>}
          <div><dt>Ingredients</dt><dd>{verifiedList(detail.ingredients)}</dd></div>
          <div><dt>Warnings</dt><dd>{verifiedList(detail.warnings)}</dd></div>
          <div><dt>Age guidance</dt><dd>{detail.age_restrictions || "Not yet verified"}</dd></div>
        </dl>
        {originalPrice && <ExchangeRateNote />}
        <a className="primary-action" href={detail.source_url} target="_blank" rel="noopener noreferrer">Open original product page ↗</a>
        <p className="detail-date">Captured {formatCaptureDate(detail.captured_at)} · Details may have changed.</p>
      </div>
    </Dialog>
  );
}

const comparisonRows: [string, (product: Product) => string][] = [
  ["Price at capture (₹)", displayPrice],
  ["Category", (product) => product.category || "Unknown"],
  ["Region", (product) => product.region],
  ["Ingredients", (product) => verifiedList(product.ingredients)],
  ["Warnings", (product) => verifiedList(product.warnings)],
];

function ComparisonDialog({ compareOpen, setCompareOpen, compared }: { compareOpen: boolean; setCompareOpen: (value: boolean) => void; compared: Product[] }) {
  if (!compareOpen) return null;
  return (
    <Dialog kind="comparison" title="compare-title" onDismiss={() => setCompareOpen(false)}>
      <h2 id="compare-title">Product comparison</h2>
      <div className="comparison-scroll">
        <table>
          <thead><tr><th scope="col">Published detail</th>{compared.map((product) => <th scope="col" key={product.id}>{product.name}<small>{product.brand}</small></th>)}</tr></thead>
          <tbody>
            {comparisonRows.map(([label, value]) => (
              <tr key={label}><th scope="row">{label}</th>{compared.map((product) => <td key={product.id}>{value(product)}</td>)}</tr>
            ))}
            <tr><th scope="row">Source</th>{compared.map((product) => <td key={product.id}><a href={product.source_url} target="_blank" rel="noopener noreferrer">Open listing ↗</a></td>)}</tr>
          </tbody>
        </table>
      </div>
      {compared.some((product) => product.currency === "USD") && <ExchangeRateNote />}
      <p>Check each original listing for current details.</p>
    </Dialog>
  );
}
