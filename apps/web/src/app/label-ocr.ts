import type { Worker } from "tesseract.js";

async function prepareImage(file: File) {
  const bitmap = await createImageBitmap(file);
  try {
    if (bitmap.width * bitmap.height > 20_000_000) {
      throw new Error("Label image dimensions exceed the limit");
    }
    const scale = Math.min(1, 2000 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Could not prepare the label image");
    context.fillStyle = "white";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    return canvas;
  } finally {
    bitmap.close();
  }
}

export async function readLabelOnDevice(file: File) {
  const image = await prepareImage(file);
  const { createWorker, OEM, PSM } = await import("tesseract.js");
  let worker: Worker | undefined;
  let finished = false;
  let timeout: ReturnType<typeof setTimeout> | undefined;

  const unavailable = new Promise<never>((_, reject) => {
    timeout = setTimeout(() => reject(new Error("Reading the label timed out")), 45_000);
  });

  // The worker can report initialization failures through errorHandler.
  const ready = new Promise<Worker>((resolve, reject) => {
    void createWorker("eng", OEM.LSTM_ONLY, {
      workerPath: "/ocr/worker.min.js",
      corePath: "/ocr",
      langPath: "/ocr",
      workerBlobURL: false,
      errorHandler: reject,
    }).then((started) => {
      if (finished) void started.terminate();
      else resolve(started);
    }, reject);
  });

  try {
    const active = await Promise.race([ready, unavailable]);
    worker = active;
    await Promise.race([active.setParameters({ tessedit_pageseg_mode: PSM.AUTO }), unavailable]);
    const { data } = await Promise.race([active.recognize(image), unavailable]);
    return data.text.trim();
  } finally {
    finished = true;
    clearTimeout(timeout);
    await worker?.terminate();
  }
}
