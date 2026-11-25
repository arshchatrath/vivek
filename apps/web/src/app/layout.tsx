import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vivek | Wellness guidance and product catalog",
  description: "Describe a concern, read guidance from health organizations, and explore official product listings.",
  robots: { index: false, follow: false },
  openGraph: { title: "Vivek | Wellness guidance and product catalog", description: "Explore sourced health guidance and official product details.", type: "website" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" data-type="software" data-ground="sage" data-tone="light" data-radius="round" data-buttons="solid" data-motion="" suppressHydrationWarning>
    <head>
      <meta name="page-type" content="software" /><meta name="site-kind" content="software" /><meta name="theme-color" content="#f8f7ef" />
      <link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@400..800&family=JetBrains+Mono:wght@400..500&display=swap" rel="stylesheet" />
      <link rel="stylesheet" href="/assets/system.css" />
      <link rel="stylesheet" href="/assets/motion/motion.css" /><link rel="stylesheet" href="/assets/backgrounds/backgrounds.css" />
      <link rel="stylesheet" href="/assets/layout/layout.css" /><link rel="stylesheet" href="/vivek.css" />
      <link rel="stylesheet" href="/catalog.css" />
      <link rel="modulepreload" href="/assets/moments/moments.js" />
      <link rel="modulepreload" href="/assets/moments/lib.js" />
      <link rel="modulepreload" href="/assets/moments/counter-rolls/moment.js" />
      <script dangerouslySetInnerHTML={{ __html: `
        const vivekRoot = document.documentElement;
        vivekRoot.classList.add('m-enter', 'mo-js', 'vivek-opening');
        setTimeout(() => vivekRoot.classList.add('m-enter-done'), 700);
        setTimeout(() => vivekRoot.classList.add('mo-safe'), 2500);
        setTimeout(() => {
          vivekRoot.classList.remove('vivek-opening');
          window.dispatchEvent(new Event('vivek:opened'));
        }, 3200);
      ` }} />
    </head>
    <body className="vivek-app" id="top">{children}<Script src="/assets/backgrounds/backgrounds.js" strategy="afterInteractive" /><Script src="/site.js" type="module" strategy="afterInteractive" /><Script src="/assets/motion/motion.js" type="module" strategy="afterInteractive" /></body>
  </html>;
}

