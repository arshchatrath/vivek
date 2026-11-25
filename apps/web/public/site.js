const root = document.documentElement;
let brokenImages = 0;

function markBroken(image) {
  if (image.hasAttribute("data-broken")) return;
  image.setAttribute("data-broken", "");
  image.setAttribute("data-placeholder", "");
  root.dataset.broken = String(++brokenImages);
}

function watchImage(image) {
  if (image.complete && image.getAttribute("src") && !image.naturalWidth) {
    image.decode().catch(() => markBroken(image));
    return;
  }
  image.addEventListener("error", () => markBroken(image), { once: true });
}

function loadProductPhotos() {
  document.querySelectorAll("img").forEach(watchImage);
  const load = () => {
    document.querySelectorAll('img[loading="lazy"]').forEach(image => {
      image.loading = "eager";
    });
  };
  const queue = () => {
    if (window.requestIdleCallback) window.requestIdleCallback(load);
    else setTimeout(load, 200);
  };
  if (document.readyState === "complete") queue();
  else window.addEventListener("load", queue, { once: true });
}

async function start() {
  loadProductPhotos();
  if (document.querySelector("[data-moment]")) {
    try {
      const { mountAll } = await import("./assets/moments/moments.js");
      await mountAll();
    } catch {
      root.classList.add("mo-safe");
    }
  }
  root.dataset.ready = "1";
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", start, { once: true });
} else {
  void start();
}
