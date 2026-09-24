// Slice a tall page screenshot into fixed-height, page-order-keyed chunks.
//
// Why: a full-page SS of a long ATS form is one huge image. Reading it whole is
// slow and imprecise. We cut it into fixed tiles, key each by its top-to-bottom
// order, and emit a manifest so the reader knows which slice is which part of the
// page ("slice-01 = top", "slice-05 = submit row") without re-deriving it.
//
// Usage:  node image_slicing.js <input.png> [outDir]
//   node image_slicing.js oracle-step4-review.png slices/
//
// Decision: tiles are full page WIDTH x SLICE_HEIGHT px. Anything taller than
// SLICE_HEIGHT is sliced; a page <= SLICE_HEIGHT stays a single slice-01. OVERLAP
// keeps a field that lands on a cut line fully visible in one of the two tiles.

const sharp = require("sharp");
const fs = require("fs").promises;
const path = require("path");

const SLICE_HEIGHT = 1400; // max px height per tile — the "beyond this, slice" threshold
const OVERLAP = 120;       // px carried into the next tile so nothing splits across a cut

async function sliceImage(inputPath, outDir = "slices") {
  const buffer = await fs.readFile(inputPath);
  const { width, height } = await sharp(buffer).metadata();
  await fs.mkdir(outDir, { recursive: true });

  const step = SLICE_HEIGHT - OVERLAP;
  // Precise, mathematical count — no drift, no empty trailing tile.
  const count = height <= SLICE_HEIGHT ? 1 : Math.ceil((height - OVERLAP) / step);
  const pad = String(count).length;

  const base = path.basename(inputPath, path.extname(inputPath));
  const manifest = { source: inputPath, width, height, sliceHeight: SLICE_HEIGHT, overlap: OVERLAP, count, slices: [] };

  for (let order = 1; order <= count; order++) {
    const top = (order - 1) * step;
    const h = Math.min(SLICE_HEIGHT, height - top);
    const key = `${base}-slice-${String(order).padStart(pad, "0")}`;
    const file = path.join(outDir, `${key}.png`);

    await sharp(buffer).extract({ left: 0, top, width, height: h }).toFile(file);

    manifest.slices.push({ key, order, file, yTop: top, yBottom: top + h, height: h });
  }

  const manifestPath = path.join(outDir, `${base}-manifest.json`);
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
  console.log(`${count} slice(s) -> ${outDir}  (manifest: ${manifestPath})`);
  return manifest;
}

const [, , inputPath, outDir] = process.argv;
if (!inputPath) {
  console.error("usage: node image_slicing.js <input.png> [outDir]");
  process.exit(1);
}
sliceImage(inputPath, outDir).catch((e) => { console.error(e); process.exit(1); });

module.exports = { sliceImage, SLICE_HEIGHT, OVERLAP };
