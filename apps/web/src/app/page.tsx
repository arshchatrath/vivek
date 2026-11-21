import seed from "../../../../data/seeds/catalog.json";
import VivekApp from "./vivek-app";

const products = seed.products.map(({
  id, brand, region, name, description, category, image_url, price, currency,
  ingredients, warnings, age_restrictions, source_url, captured_at,
}) => ({
  id, brand, region, name, description, category, image_url, price, currency,
  ingredients, warnings, age_restrictions, source_url, captured_at,
}));

export default function Home() {
  return <VivekApp products={products} generatedAt={seed.generated_at} coverage={seed.coverage} />;
}

