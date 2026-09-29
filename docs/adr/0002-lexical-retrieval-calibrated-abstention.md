# ADR 0002: Lexical (BM25) retrieval over heading passages, with a corpus-calibrated "no confident match" threshold

> Architecture Decision Record. Owned by the Architect. It stays **proposed** until
> docs-retrieval-core's Release Gate shows the eval bar is met, and it becomes
> accepted then. While proposed it may be revised (the overfitting protocol allows
> a bounded, versioned method change after a failed gate). Once accepted, a change
> needs a new ADR that supersedes it.

- **Status:** proposed
- **Date:** 2026-09-28
- **Slice:** `runs/docs-retrieval/` (docs-retrieval-core). The full specification,
  including every parameter, is `runs/docs-retrieval/02-tech-spec.md`, section
  "Retrieval".

## Context

The intent asks retrieval to return up to 5 passages, each with its file, heading
and line range, **or "no confident match" rather than the least-bad passages**
(Done-means 4 and 5). It must reach at least 80% on the owner's eval set, and at
least 80% of the unanswerable questions must abstain (Done-means 8). The
unanswerable ones include hard negatives whose keywords appear in the docs in an
unrelated sense. No model may be called, and dependencies should be as few as
possible. The product stance is "grounded or silent". The repo is a template,
so whatever decides confidence has to work on someone else's docs too, not just
Aveto's.

## Decision

- **Passages are ATX-heading sections.** One section is one passage. Headings
  inside code fences and front matter are ignored. There is no size-based
  splitting, so "path + heading + line range" is always an exact citation.
- **Ranking is BM25**, with k1 = 1.2 and b = 0.75. Each passage is scored as body
  tokens, plus its heading trail counted twice, plus its file path counted once,
  a simple approximation of BM25F. The tokenizer casefolds, splits on
  non-alphanumerics, removes the NLTK English stopword list, and folds plurals
  with Harman's S-stemmer. There is no synonym table. A file contributes at most
  2 of the top 5 passages.
- **Confidence is the idf-weighted fraction of the question's terms that the top
  passage contains** ("coverage", in [0, 1]). Terms that appear nowhere in the
  docs stay in the denominator at maximal weight: if what you asked about is not
  in the docs, the docs do not answer you.
- **The threshold τ is calibrated from the corpus at ingest time.** It is the
  90th percentile of coverage over 2000 seeded "cross-file null" questions. Each
  null question uses 2–5 real words, each drawn from a different file, so every
  word is in the docs but no passage answers the combination. τ is stored in the
  index. Below τ, *no* passages are returned.
- **Every parameter is pre-registered** in the tech spec before the eval set is
  run. The eval set is a test, never a tuning set. Each run is committed, and a
  miss is a failed gate handled by a bounded, versioned method revision, not by
  adjusting knobs.

## Alternatives considered

- **Embeddings (a local sentence-transformer, or an embeddings API).** These
  would likely help with paraphrased questions. A local model means large
  dependencies (torch or onnxruntime, plus a model download, which is network
  access outside the approval). An API means a model call, which the intent rules
  out for this slice. Kept as the owner's option if lexical retrieval cannot meet
  the bar.
- **The `rank-bm25` library, or scikit-learn TF-IDF.** These pull in numpy (and
  scipy), and they hide the per-term scores the coverage signal needs. Our BM25 is
  about 60 lines.
- **A fixed, hand-picked score threshold.** BM25 scores are unbounded and depend
  on the question, so one cut-off means different things for different questions.
  A constant picked for Aveto's docs would not carry over to an adopter's docs,
  and picking it would in practice mean tuning it against the eval set.
- **A relative-margin rule (top score versus the second).** This measures
  ambiguity between passages, not whether any passage answers the question. A
  hard negative can have one clear, wrong winner.
- **Fixed-size chunks instead of heading sections.** Citations would lose the
  heading, and chunks would cut across the author's own structure. Rejected,
  because provenance is a "must not break".
- **Porter stemming.** Its more aggressive folding merges unrelated words, which
  works against hard negatives. Plural folding is the conservative choice.

## Consequences

- **Easier:** no runtime dependencies. Retrieval is fully deterministic and fast.
  Every result explains itself (coverage against τ). Pointing the tool at new
  docs re-calibrates automatically. The drafting slice gets a `RetrievalResult`
  whose `hits` is empty whenever it should not draft.
- **Harder:** paraphrases with no shared vocabulary are missed, and the same word
  used in different senses cannot be told apart lexically. The threshold trades
  answerable recall against abstention, and the trade is decided in advance (p90,
  half the owner's tolerated error), not optimised.
- **Revisit if:** the eval bar is missed after the bounded retries, a fresh
  owner-written question set shows the score does not generalise, or the drafting
  slice's checker reports that confident retrievals often lack the answer. Any of
  these would motivate an embeddings ADR. That ADR carries its own dependency
  cost, and a model call if one is involved.
