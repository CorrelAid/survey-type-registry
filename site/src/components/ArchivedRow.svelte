<script lang="ts">
  import type { RegistryEntry } from "../data/registry";

  interface Props { entry: RegistryEntry; }
  let { entry }: Props = $props();
</script>

<div style="margin-bottom: 0.75rem;">
  <strong>{entry["skos:prefLabel"] ?? entry["@id"]}</strong>
  <code>{entry.xlsform?.typeString ?? entry["@id"]}</code>
  <span class="tier-badge tier-archived">archived</span>
  {#if entry.archivedSince}<span style="font-size: 0.85em; color: color-mix(in srgb, var(--color-text-primary) 60%, transparent);"> · {entry.archivedSince}</span>{/if}
  {#if entry.archiveReason}
    <p style="font-size: 0.9rem; margin: 0.25rem 0 0;">{entry.archiveReason}</p>
  {:else if entry.transformation && (entry.transformation as { warnings?: string[] }).warnings?.length}
    <p style="font-size: 0.9rem; margin: 0.25rem 0 0;">
      {(entry.transformation as { warnings: string[] }).warnings.join(" · ")}
    </p>
  {/if}
</div>
