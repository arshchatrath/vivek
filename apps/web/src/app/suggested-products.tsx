"use client";

import { useId } from "react";
import { displayPrice, formatCaptureDate } from "./catalog-display";

export type ListingSummary = {
  id: string;
  brand: string;
  name: string;
  source_url: string;
  captured_at: string;
  availability?: string | null;
  image_url?: string | null;
  price?: number | null;
  currency?: string | null;
};

export type ProductSuggestion = {
  listing: ListingSummary;
  reasons?: { name: string; form: string; evidence: { title: string; url: string } }[];
  citation?: number;
};

export default function SuggestedProducts({ products, title = "Suggested products", note }: {
  products: ProductSuggestion[];
  title?: string;
  note?: string;
}) {
  const heading = useId();
  return <section className="suggested-products" aria-labelledby={heading}>
    <h3 id={heading}>{title}</h3>
    {products.length ? <>
      {note && <p className="suggestion-note">{note}</p>}
      <ul className="suggestion-list">
        {products.map(({ listing, reasons, citation }) => <li key={listing.id} className="suggestion-card">
          <div className="suggestion-photo" aria-hidden="true">
            <span>{listing.brand}</span>
            {listing.image_url && <img src={listing.image_url} alt="" loading="lazy"
              onLoad={(event) => { event.currentTarget.dataset.ready = "true"; }}
              onError={(event) => { event.currentTarget.hidden = true; }} />}
          </div>
          <div className="suggestion-content">
            <div className="suggestion-brand">{citation && <span>[{citation}] </span>}{listing.brand}</div>
            <h4>{listing.name}</h4>
            <p className="suggestion-price">{displayPrice(listing)}</p>
            {listing.availability === "OutOfStock" && <p className="suggestion-stock">Out of stock at capture</p>}
          </div>
          {reasons?.length ? <div className="suggestion-reasons">
            {reasons.map(({ name, form, evidence }) => <p key={name}>
              <strong>{name}</strong> <span>· {form}</span>
              <a href={evidence.url} target="_blank" rel="noopener noreferrer" aria-label={evidence.title}>Guidance ↗</a>
            </p>)}
          </div> : null}
          <div className="suggestion-footer">
            <a href={listing.source_url} target="_blank" rel="noopener noreferrer" aria-label={`View ${listing.name} listing`}>View listing ↗</a>
            <small>Captured {formatCaptureDate(listing.captured_at)}</small>
          </div>
        </li>)}
      </ul>
    </> : <p className="suggestion-empty">No checked product matches this guide yet. You can still read the guidance and its sources below.</p>}
  </section>;
}
