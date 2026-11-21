"use client";

import { useEffect, useRef } from "react";

export default function OpeningScreen() {
  const screen = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = screen.current;
    if (!dialog || !document.documentElement.classList.contains("vivek-opening")) return;

    const finish = () => dialog.close();
    dialog.showModal();
    window.addEventListener("vivek:opened", finish, { once: true });
    return () => {
      window.removeEventListener("vivek:opened", finish);
      finish();
    };
  }, []);

  function dismiss() {
    document.documentElement.classList.remove("vivek-opening");
    screen.current?.close();
  }

  return (
    <dialog ref={screen} className="opening-screen" aria-label="Opening Vivek" onCancel={(event) => {
      event.preventDefault();
      dismiss();
    }}>
      <div className="opening-content">
        <div className="opening-brand" aria-hidden="true"><span>✳</span>vivek.</div>
        <p>Opening your wellness guide</p>
        <div className="opening-progress" aria-hidden="true" />
      </div>
      <button type="button" className="opening-skip" onClick={dismiss}>Skip intro</button>
    </dialog>
  );
}
