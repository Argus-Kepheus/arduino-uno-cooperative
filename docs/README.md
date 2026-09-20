# Documentation / Documentação

- [English](EN/README.md)
- [Português](PT/README.md)

This directory contains the maintained multilingual technical documentation for
`arduino-uno-cooperative`.

Esta pasta contém a documentação técnica multilíngue mantida do
`arduino-uno-cooperative`.

## Language governance

- **English (EN)** is the canonical narrative language.
- **Portuguese (PT-BR)** is a maintained translation.
- Technical configuration facts remain canonical under `config/`; the
  documentation explains them but does not become a competing configuration
  source.
- `report/` remains a historical/academic snapshot and is outside the live
  documentation parity contract.

The machine-readable contract is [`metadata.json`](metadata.json).

## Semantic parity

Each maintained document begins with:

```text
<!-- doc-id: ... -->
<!-- language: EN or PT -->
<!-- content-revision: ... -->
```

Semantic sections are identified independently of translated headings:

```text
<!-- section: registration-order -->
## Registration order
```

and:

```text
<!-- section: registration-order -->
## Ordem de registro
```

This means EN/PT headings and prose may be natural in each language while both
documents still expose the same required concepts.

For each `doc-id`, `docs/metadata.json` defines:

- the current shared `content_revision`;
- the path of each maintained language;
- the required semantic-section sequence.

A change that materially changes one document must update the corresponding
translation and advance the shared revision together.

## Current document set

| doc-id | EN | PT |
|---|---|---|
| `project-overview` | `EN/README.md` | `PT/README.md` |
| `architecture` | `EN/architecture.md` | `PT/architecture.md` |
| `displays` | `EN/displays.md` | `PT/displays.md` |
| `pinout` | `EN/pinout.md` | `PT/pinout.md` |
| `scheduler` | `EN/scheduler.md` | `PT/scheduler.md` |
| `technical-specification` | `EN/technical-specification.md` | `PT/technical-specification.md` |
| `validation-checklist` | `EN/validation-checklist.md` | `PT/validation-checklist.md` |

## Validation

Run:

```text
python tools/validate_repository.py
```

The repository validator rejects:

- a missing registered document;
- an incorrect `doc-id` or language marker;
- EN/PT revision drift;
- a missing, extra, duplicated or reordered required semantic section;
- a metadata path that does not cover every maintained language.

Wave 4 establishes parity governance only. Numeric/documentation deduplication
and generated documentation regions are intentionally deferred to Wave 5.
