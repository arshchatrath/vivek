"use client";

import { useEffect } from "react";

export default function ProductMotion() {
  useEffect(() => {
    const media = window.matchMedia("(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)");
    let cleanup: (() => void) | undefined;
    let mounted = true;

    async function lift(event: PointerEvent) {
      if (!media.matches || event.pointerType === "touch") return;
      const frame = (event.target as Element | null)?.closest<HTMLElement>(".product-shelf .product-photo, .tool-visual, .source-visual-link");
      const image = frame?.querySelector("img");
      if (!frame || !image || (event.relatedTarget instanceof Node && frame.contains(event.relatedTarget))) return;
      const { gsap } = await import("gsap");
      if (!mounted || !media.matches || !frame.matches(":hover")) return;
      cleanup?.();

      frame.classList.add("motion-tilted");
      const motion = gsap.context(() => {
        const easing = { duration: .42, ease: "power3.out" };
        gsap.set(image, { transformPerspective: 700 });
        const pitch = gsap.quickTo(image, "rotationX", easing);
        const yaw = gsap.quickTo(image, "rotationY", easing);
        const rise = gsap.quickTo(image, "y", easing);

        const move = (pointer: PointerEvent) => {
          const bounds = frame.getBoundingClientRect();
          pitch((.5 - (pointer.clientY - bounds.top) / bounds.height) * 12);
          yaw(((pointer.clientX - bounds.left) / bounds.width - .5) * 16);
          rise(-5);
        };

        function rest() {
          pitch(0);
          yaw(0);
          rise(0);
        }

        move(event);
        frame.addEventListener("pointermove", move);
        frame.addEventListener("pointerleave", rest);
        return () => {
          frame.removeEventListener("pointermove", move);
          frame.removeEventListener("pointerleave", rest);
        };
      });
      cleanup = () => {
        motion.revert();
        frame.classList.remove("motion-tilted");
      };
    }

    function syncPreference() {
      if (!media.matches) cleanup?.();
    }

    document.addEventListener("pointerover", lift);
    media.addEventListener("change", syncPreference);
    return () => {
      mounted = false;
      cleanup?.();
      media.removeEventListener("change", syncPreference);
      document.removeEventListener("pointerover", lift);
    };
  }, []);

  return null;
}
