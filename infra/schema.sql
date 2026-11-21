CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS catalog_products (
  id uuid PRIMARY KEY,
  brand text NOT NULL,
  region text NOT NULL,
  name text NOT NULL,
  description text,
  sku text,
  category text,
  image_url text,
  price numeric(12,2),
  currency char(3),
  availability text,
  ingredients jsonb,
  warnings jsonb,
  age_restrictions text,
  source_url text NOT NULL UNIQUE,
  captured_at timestamptz NOT NULL,
  content_sha256 char(64) NOT NULL,
  review_status text NOT NULL CHECK (review_status IN ('source_observed','needs_review','approved','retired')),
  field_sources jsonb NOT NULL,
  search_vector tsvector GENERATED ALWAYS AS
    (to_tsvector('english', coalesce(name,'') || ' ' || coalesce(brand,'') || ' ' || coalesce(category,'') || ' ' || coalesce(description,''))) STORED
);
CREATE INDEX IF NOT EXISTS idx_catalog_search ON catalog_products USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_catalog_name_trgm ON catalog_products USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_catalog_brand ON catalog_products(brand);

CREATE TABLE IF NOT EXISTS source_documents (
  id uuid PRIMARY KEY,
  source_url text NOT NULL,
  title text NOT NULL,
  publisher text NOT NULL,
  jurisdiction text,
  source_kind text NOT NULL,
  rights_status text NOT NULL,
  captured_at timestamptz NOT NULL,
  content_sha256 char(64) NOT NULL,
  review_status text NOT NULL,
  UNIQUE(source_url, content_sha256)
);
CREATE TABLE IF NOT EXISTS source_passages (
  id uuid PRIMARY KEY,
  document_id uuid NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
  passage text NOT NULL,
  passage_index integer NOT NULL,
  embedding vector(384),
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED,
  UNIQUE(document_id, passage_index)
);
CREATE INDEX IF NOT EXISTS idx_passage_search ON source_passages USING gin(search_vector);
CREATE INDEX IF NOT EXISTS idx_passage_embedding ON source_passages USING hnsw(embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS concern_passages (
  topic text NOT NULL,
  passage_key text NOT NULL,
  position integer NOT NULL,
  passage text NOT NULL,
  source_url text NOT NULL,
  reviewed_on date NOT NULL,
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED,
  PRIMARY KEY (topic, passage_key)
);
CREATE INDEX IF NOT EXISTS idx_concern_search ON concern_passages USING gin(search_vector);

CREATE TABLE IF NOT EXISTS concern_topics (
  topic text PRIMARY KEY,
  profile text NOT NULL,
  embedding vector(384) NOT NULL,
  search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', profile)) STORED
);

CREATE TABLE IF NOT EXISTS catalog_change_events (
  id bigserial PRIMARY KEY,
  product_id uuid NOT NULL,
  previous_hash char(64),
  new_hash char(64) NOT NULL,
  detected_at timestamptz NOT NULL DEFAULT now(),
  state text NOT NULL DEFAULT 'needs_review',
  diff jsonb NOT NULL DEFAULT '{}'::jsonb
);

