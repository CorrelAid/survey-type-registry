// Build-time data loader. Vite resolves `?raw` and JSON imports of files
// under `@registry/` (alias to ../ in vite.config.ts).
//
// Two roots:
//   - ../survey-types.jsonld    main jsonld with conventions/vocab/etc.
//   - ../types/<slug>/definition.jsonld  blessed QuestionType definitions
//   - ../archived/survey-types.archived.jsonld  archived list (read for the
//     "rejected" section)

// .jsonld files are imported as raw text and JSON.parsed because Vite only
// auto-parses .json by extension.
import mainGraphRaw from "@registry/survey-types.jsonld?raw";
import archivedGraphRaw from "@registry/archived/survey-types.archived.jsonld?raw";

const mainGraph = JSON.parse(mainGraphRaw) as { "@graph": RegistryEntry[] };
const archivedGraph = JSON.parse(archivedGraphRaw) as { "@graph": RegistryEntry[] };

// Vite glob: types/<slug>/definition.jsonld (raw, parsed below)
const typeDefsRaw = import.meta.glob<string>(
  "@registry/types/*/definition.jsonld",
  { eager: true, query: "?raw", import: "default" }
);
const typeDefs: Record<string, { "@graph": RegistryEntry[] }> = {};
for (const [k, v] of Object.entries(typeDefsRaw)) {
  typeDefs[k] = JSON.parse(v as string);
}

// Variant payloads: examples/<id>/{xlsform.json, ddi.xml, tsv.tsv, meta.json}
const exampleXlsforms = import.meta.glob<{ default: ExampleXlsform }>(
  "@registry/types/*/examples/*/xlsform.json",
  { eager: true }
);
const exampleDdi = import.meta.glob<string>(
  "@registry/types/*/examples/*/ddi.xml",
  { eager: true, query: "?raw", import: "default" }
);
const exampleTsv = import.meta.glob<string>(
  "@registry/types/*/examples/*/tsv.tsv",
  { eager: true, query: "?raw", import: "default" }
);
const exampleMeta = import.meta.glob<{ default: ExampleMeta }>(
  "@registry/types/*/examples/*/meta.json",
  { eager: true }
);

export interface RegistryEntry {
  "@id": string;
  "@type": string;
  "skos:prefLabel"?: string;
  tier?: string;
  frozenSince?: string;
  xlsform?: { typeString?: string; aliases?: string[]; requiresListName?: boolean };
  limesurvey?: { typeCode?: string | null; supportsOther?: boolean; answerClass?: string | null };
  ddi?: Record<string, unknown>;
  concept?: { openness?: string; cardinality?: string; dataNature?: string };
  qwacback?: { answerType?: string; hasLongList?: boolean };
  constraints?: Record<string, unknown>;
  transformation?: Record<string, unknown>;
  variants?: string[];
  // PresentationVariant fields
  examplePath?: string;
  exampleDir?: string;
  presentation?: Record<string, unknown>;
  "skos:broader"?: { "@id": string } | { "@id": string }[];
  // Composite fields
  trigger?: Record<string, unknown>;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  schematronPatterns?: string[];
  notes?: string[];
  // GlobalConvention
  rule?: Record<string, unknown>;
  // XLSFormColumnMap
  map?: Record<string, unknown>[];
  // Vocabulary
  xlsformFilename?: string;
  ddiVocab?: string;
  vocabURI?: string;
  standard?: string;
  description?: string;
  // Archive metadata
  archiveReason?: string;
  archivedSince?: string;
}

export interface ExampleXlsform {
  survey: Array<Record<string, string>>;
  choices: Array<Record<string, string>>;
}

export interface ExampleMeta {
  id: string;
  variantId: string;
  label?: string;
  answerType?: string | null;
  concept?: Record<string, string>;
  presentation?: Record<string, unknown>;
  broader?: string;
}

function loadEntries(): RegistryEntry[] {
  const all: RegistryEntry[] = [];
  all.push(...(mainGraph["@graph"] ?? []));
  for (const sub of Object.values(typeDefs)) {
    all.push(...(sub["@graph"] ?? []));
  }
  return all;
}

export const ENTRIES: RegistryEntry[] = loadEntries();
export const ARCHIVED: RegistryEntry[] = archivedGraph["@graph"] ?? [];

export const QUESTION_TYPES = ENTRIES.filter(e => e["@type"] === "QuestionType");
export const STRUCTURAL_TYPES = ENTRIES.filter(e => e["@type"] === "StructuralType");
export const METADATA_TYPES = ENTRIES.filter(e => e["@type"] === "MetadataType");
export const PRESENTATION_VARIANTS = ENTRIES.filter(e => e["@type"] === "PresentationVariant");
export const APPEARANCES = ENTRIES.filter(e => e["@type"] === "Appearance");
export const CONVENTIONS = ENTRIES.filter(e => e["@type"] === "GlobalConvention");
export const COMPOSITES = ENTRIES.filter(e => e["@type"] === "Composite");
export const VOCABULARIES = ENTRIES.filter(e => e["@type"] === "Vocabulary");

export const BLESSED = ENTRIES.filter(e => e.tier === "v1-blessed");

// Examples keyed by variant slug (e.g. "single_choice", "grid")
export interface VariantBundle {
  variantId: string;
  slug: string;
  xlsform: ExampleXlsform | null;
  ddi: string | null;
  tsv: string | null;
  meta: ExampleMeta | null;
}

function variantSlugFromPath(path: string): string {
  // e.g. /home/.../types/select_one/examples/single_choice_other/xlsform.json
  const m = path.match(/examples\/([^/]+)\//);
  return m ? m[1] : "";
}

export function getVariantBundle(slug: string): VariantBundle | null {
  let xlsform: ExampleXlsform | null = null;
  let ddi: string | null = null;
  let tsv: string | null = null;
  let meta: ExampleMeta | null = null;

  for (const [path, mod] of Object.entries(exampleXlsforms)) {
    if (variantSlugFromPath(path) === slug) {
      xlsform = (mod as { default: ExampleXlsform }).default;
      break;
    }
  }
  for (const [path, content] of Object.entries(exampleDdi)) {
    if (variantSlugFromPath(path) === slug) {
      ddi = content as string;
      break;
    }
  }
  for (const [path, content] of Object.entries(exampleTsv)) {
    if (variantSlugFromPath(path) === slug) {
      tsv = content as string;
      break;
    }
  }
  for (const [path, mod] of Object.entries(exampleMeta)) {
    if (variantSlugFromPath(path) === slug) {
      meta = (mod as { default: ExampleMeta }).default;
      break;
    }
  }

  if (!xlsform && !ddi && !tsv) return null;
  return {
    variantId: `variant:${slug}`,
    slug,
    xlsform,
    ddi,
    tsv,
    meta,
  };
}

export function variantsForType(typeId: string): VariantBundle[] {
  const variants = PRESENTATION_VARIANTS.filter(v => {
    const broader = v["skos:broader"];
    if (!broader) return false;
    const ids = Array.isArray(broader) ? broader.map(b => b["@id"]) : [broader["@id"]];
    return ids.includes(typeId);
  });
  return variants
    .map(v => getVariantBundle(v["@id"].split(":", 2)[1]))
    .filter((b): b is VariantBundle => b !== null);
}
