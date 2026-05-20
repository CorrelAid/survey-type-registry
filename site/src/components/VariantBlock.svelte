<script lang="ts">
  import type { VariantBundle } from "../data/registry";

  interface Props { variant: VariantBundle; }
  let { variant }: Props = $props();

  type TabKey = "xlsform" | "ddi" | "tsv";
  let active: TabKey = $state("xlsform");

  function tabClass(k: TabKey): string {
    return active === k ? "tab-btn active" : "tab-btn";
  }

  // Render the xlsform.json's survey + choices as HTML tables
  function renderTable(rows: Array<Record<string, string>>): string {
    if (!rows?.length) return "<em>empty</em>";
    const headers = [...new Set(rows.flatMap(r => Object.keys(r)))];
    const head = headers.map(h => `<th>${h}</th>`).join("");
    const body = rows
      .map(r => `<tr>${headers.map(h => `<td>${(r[h] ?? "").toString().replace(/</g, "&lt;")}</td>`).join("")}</tr>`)
      .join("");
    return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
  }
</script>

<div class="variant-block">
  <div class="variant-header">
    <strong>{variant.meta?.label ?? variant.slug}</strong>
    <code>{variant.slug}</code>
  </div>

  <div class="tabs">
    <button class={tabClass("xlsform")} onclick={() => (active = "xlsform")}>XLSForm</button>
    {#if variant.ddi}<button class={tabClass("ddi")} onclick={() => (active = "ddi")}>DDI XML</button>{/if}
    {#if variant.tsv}<button class={tabClass("tsv")} onclick={() => (active = "tsv")}>LimeSurvey TSV</button>{/if}
  </div>

  <div class="tab-body">
    {#if active === "xlsform" && variant.xlsform}
      <div><strong>survey</strong>{@html renderTable(variant.xlsform.survey)}</div>
      {#if variant.xlsform.choices?.length}
        <div style="margin-top: 0.5rem;"><strong>choices</strong>{@html renderTable(variant.xlsform.choices)}</div>
      {/if}
    {/if}
    {#if active === "ddi" && variant.ddi}
      <pre>{variant.ddi}</pre>
    {/if}
    {#if active === "tsv" && variant.tsv}
      <pre>{variant.tsv}</pre>
    {/if}
  </div>
</div>

<style>
  .variant-block {
    margin: 0.75rem 0;
    border: 1px solid color-mix(in srgb, var(--color-text-primary) 15%, transparent);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }
  .variant-header {
    padding: 0.5rem 0.75rem;
    background: color-mix(in srgb, var(--color-text-primary) 4%, transparent);
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
  }
  .tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid color-mix(in srgb, var(--color-text-primary) 10%, transparent);
  }
  .tab-btn {
    padding: 0.35rem 0.75rem;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    font-family: var(--font-family-body);
    cursor: pointer;
    color: color-mix(in srgb, var(--color-text-primary) 65%, transparent);
  }
  .tab-btn.active {
    color: var(--color-text-primary);
    border-bottom-color: var(--color-text-primary);
  }
  .tab-body {
    padding: 0.75rem;
  }
  .tab-body :global(table) {
    font-size: 0.85rem;
  }
</style>
