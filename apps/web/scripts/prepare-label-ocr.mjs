import { copyFile, mkdir } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);
const tesseract = dirname(require.resolve("tesseract.js/package.json"));
const core = dirname(require.resolve("tesseract.js-core/package.json", { paths: [tesseract] }));
const english = dirname(require.resolve("@tesseract.js-data/eng/package.json"));
const output = new URL("../public/ocr/", import.meta.url);

// Match the LSTM core variants selected by the browser worker.
const coreFiles = ["", "-simd", "-relaxedsimd"].map((variant) => `tesseract-core${variant}-lstm.wasm.js`);
await mkdir(output, { recursive: true });
await Promise.all([
  ...coreFiles.map((file) => copyFile(join(core, file), new URL(file, output))),
  copyFile(join(tesseract, "dist/worker.min.js"), new URL("worker.min.js", output)),
  copyFile(join(english, "4.0.0_best_int/eng.traineddata.gz"), new URL("eng.traineddata.gz", output)),
  copyFile(join(tesseract, "LICENSE.md"), new URL("tesseract-license.txt", output)),
  copyFile(join(core, "LICENSE"), new URL("tesseract-core-license.txt", output)),
]);
