export const usdReference = { inr: 92.9699, date: "20 Nov 2026", url: "https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx" };

const rupees = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", minimumFractionDigits: 0 });
const dates = new Intl.DateTimeFormat("en-IN", { day: "numeric", month: "short", year: "numeric" });

export function displayPrice({ price, currency }: { price?: number | null; currency?: string | null }) {
  if (typeof price !== "number") return "Price unknown";
  if (currency === "INR") return rupees.format(price);
  if (currency === "USD") return `${rupees.format(Math.round(price * usdReference.inr))} (est.)`;
  return "Check listing";
}

export function formatCaptureDate(value: string) {
  return dates.format(new Date(value));
}
