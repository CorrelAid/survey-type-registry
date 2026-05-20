<script lang="ts">
  import { BLESSED, COMPOSITES, CONVENTIONS, ARCHIVED, VOCABULARIES } from "./data/registry";
  import TypeCard from "./components/TypeCard.svelte";
  import CompositeCard from "./components/CompositeCard.svelte";
  import ConventionCard from "./components/ConventionCard.svelte";
  import ArchivedRow from "./components/ArchivedRow.svelte";
</script>

<div class="layout">
  <aside class="sidebar">
    <h2>Overview</h2>
    <a href="#intro">Introduction</a>
    <a href="#layers">Three layers</a>

    <h2>v1-blessed types</h2>
    {#each BLESSED as t (t["@id"])}
      <a href={`#type-${t.xlsform?.typeString}`}>{t["skos:prefLabel"] ?? t["@id"]}</a>
    {/each}

    <h2>Composites</h2>
    {#each COMPOSITES as c (c["@id"])}
      <a href={`#composite-${c["@id"].split(":", 2)[1]}`}>{c["skos:prefLabel"] ?? c["@id"]}</a>
    {/each}

    <h2>Conventions</h2>
    {#each CONVENTIONS as conv (conv["@id"])}
      <a href={`#convention-${conv["@id"].split(":", 2)[1]}`}>{conv["skos:prefLabel"] ?? conv["@id"]}</a>
    {/each}

    {#if VOCABULARIES.length > 0}
      <h2>Vocabularies</h2>
      {#each VOCABULARIES as v (v["@id"])}
        <a href={`#vocab-${v.ddiVocab}`}>{v["skos:prefLabel"] ?? v["@id"]}</a>
      {/each}
    {/if}

    <h2>Archived</h2>
    <a href="#archived">All rejected types</a>
  </aside>

  <main>
    <section id="intro">
      <h1>CDL Survey Schema Registry</h1>
      <p>
        Single source of truth for how question types behave across the CDL survey toolchain —
        from XLSForm authoring through LimeSurvey collection to DDI-Codebook archival.
      </p>
      <p>
        This site renders the registry's content. The registry itself lives at
        <a href="https://github.com/CorrelAid/survey-type-registry"
          >github.com/CorrelAid/survey-type-registry</a
        >.
      </p>
    </section>

    <section id="layers">
      <h2>Three layers</h2>
      <p>
        The registry models survey content at three levels of granularity. Keep them
        straight when reading per-type pages.
      </p>
      <table>
        <thead>
          <tr>
            <th>Layer</th>
            <th>Unit</th>
            <th>Defined by</th>
            <th>Example</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Atom</td>
            <td>DDI <code>&lt;var&gt;</code> = 1 dataset column</td>
            <td>DDI 2.5 XSD</td>
            <td><code>V_alter</code></td>
          </tr>
          <tr>
            <td>Type-primitive</td>
            <td><code>QuestionType</code> (1 XLSForm row → 1+ vars)</td>
            <td>registry</td>
            <td><code>select_one</code> (1→1), <code>select_multiple</code> (1→N)</td>
          </tr>
          <tr>
            <td>Composite</td>
            <td><code>Composite</code> (N rows OR N vars grouped)</td>
            <td>registry</td>
            <td><code>grid</code>, <code>other_pattern</code></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>v1-blessed types</h2>
      <p>
        Self-contained folders under <code>types/&lt;slug&gt;/</code>. Each entry is frozen since the
        date noted; breaking changes require a major version bump.
      </p>
      {#each BLESSED as t (t["@id"])}
        <TypeCard type={t} />
      {/each}
    </section>

    <section>
      <h2>Composites</h2>
      <p>
        Multi-row or multi-var structural patterns. Each declares its input row roles + cardinalities,
        output structure, and the schematron patterns enforcing it.
      </p>
      {#each COMPOSITES as c (c["@id"])}
        <CompositeCard composite={c} />
      {/each}
    </section>

    <section>
      <h2>Conventions</h2>
      <p>
        Cross-cutting rules that don't fit per-type metadata. Codegen emits these to
        <code>generated/conventions.json</code>.
      </p>
      {#each CONVENTIONS as conv (conv["@id"])}
        <ConventionCard convention={conv} />
      {/each}
    </section>

    {#if VOCABULARIES.length > 0}
      <section>
        <h2>External code lists</h2>
        <p>
          Named vocabularies referenced by <code>select_X_from_file &lt;vocab&gt;.csv</code> via the
          <code>concept/@vocab</code> convention.
        </p>
        {#each VOCABULARIES as v (v["@id"])}
          <div id={`vocab-${v.ddiVocab}`} style="margin-bottom: 1rem;">
            <h3>{v["skos:prefLabel"]}</h3>
            <dl class="kv-table">
              <dt>XLSForm filename</dt><dd><code>{v.xlsformFilename}</code></dd>
              <dt>DDI <code>vocab</code></dt><dd><code>{v.ddiVocab}</code></dd>
              <dt>Standard</dt><dd>{v.standard}</dd>
              <dt>URI</dt><dd><a href={v.vocabURI}>{v.vocabURI}</a></dd>
              {#if v.description}<dt>Notes</dt><dd>{v.description}</dd>{/if}
            </dl>
          </div>
        {/each}
      </section>
    {/if}

    <section id="archived">
      <h2>Archived</h2>
      <p>
        XLSForm types recognized by the spec but rejected from the CDL ecosystem. Listed for
        contributor context. Not loaded by codegen.
      </p>
      {#each ARCHIVED as a (a["@id"])}
        <ArchivedRow entry={a} />
      {/each}
    </section>
  </main>
</div>
