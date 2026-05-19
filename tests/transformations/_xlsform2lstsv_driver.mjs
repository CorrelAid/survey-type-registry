#!/usr/bin/env node
/**
 * Bridge: read JSON {survey, choices, settings} from stdin → write LS TSV to stdout.
 *
 * Resolves xlsform2lstsv via env var XLSFORM2LSTSV_PATH (default: sibling dir).
 *
 * Usage: node _xlsform2lstsv_driver.mjs < payload.json > out.tsv
 */
import { pathToFileURL, fileURLToPath } from "node:url";
import { resolve, dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

// Default: registry-repo-root/../xlsform2lstsv (sibling layout)
const PKG_PATH = process.env.XLSFORM2LSTSV_PATH
  || resolve(__dirname, "../../../xlsform2lstsv");

const entry = resolve(PKG_PATH, "dist/index.js");
const mod = await import(pathToFileURL(entry).href);
const { XLSFormToTSVConverter } = mod;

// Silence converter's console.log/warn so only TSV reaches stdout.
console.log = (...a) => process.stderr.write(a.join(" ") + "\n");
console.warn = console.log;
console.info = console.log;

const payload = JSON.parse(await readStdin());
const survey = payload.survey || [];
const choices = payload.choices || [];
const settings = payload.settings || [];

const converter = new XLSFormToTSVConverter();
const tsv = await converter.convert(survey, choices, settings);
process.stdout.write(tsv);
