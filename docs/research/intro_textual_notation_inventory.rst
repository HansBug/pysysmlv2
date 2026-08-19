Intro to SysML v2 Textual Notation Inventory
============================================

This is the manually reviewed inventory for the official training deck
``Intro to the SysML v2 Language-Textual Notation.pdf``. The complete
machine-readable ledger is ``intro_textual_notation_inventory.json`` in this
directory. It is a research source ledger, not a parser or AST oracle.

Source
------

The reviewed source is the ``master`` file at commit
``de1070ae8e79c21532b8004fc663d47b35d0e9fa`` (release ``2026-05``):

* URL: ``https://raw.githubusercontent.com/Systems-Modeling/SysML-v2-Release/de1070ae8e79c21532b8004fc663d47b35d0e9fa/doc/Intro%20to%20the%20SysML%20v2%20Language-Textual%20Notation.pdf``
* Git blob SHA: ``e355535bb6c4d0f9d3dd1ddb9b69da06fc41fd1c``
* SHA-256: ``0d9df8880314a58ecb7aecf3ed3da9075957c30ee59f9b686358f53a3af7be4d``
* Retrieved and visually reviewed: ``2026-08-19``
* PDF size/pages: ``24,083,409`` bytes / ``185`` slides

The deck itself states that it is Copyright 2019-2026 Model Driven Solutions,
Inc. and licensed under CC BY 4.0. Preserve that notice when redistributing
the short transcriptions.

Review method and counts
------------------------

All 185 rendered pages were checked slide-by-slide. ``pdftotext`` and
``pdftohtml`` were used only to locate text and assist transcription; they did
not determine source boundaries. The ledger records:

* ``167`` slides with textual code panels;
* ``104`` closed panels marked as direct fixture candidates;
* ``62`` context/template or visibly incomplete panels;
* ``1`` opaque action containing external Alf text, marked non-fixture;
* ``5`` slides with diagram-only code-like labels and no textual source panel;
* ``13`` cover, architecture, section-divider, or library-divider slides with
  no textual code panel.

Code excerpts normalize presentation-only curly single-quote glyphs to ASCII
apostrophes, typographic ellipses to ``...``, and typographic dashes inside
code to ASCII hyphens. Slide titles retain their printed punctuation.

Explanatory-comment policy
--------------------------

The ``intro_manual_notes_5_46.json``, ``intro_manual_notes_47_185.json``, and
``intro_manual_notes_121_185.json`` ledgers are hand-authored from the
rendered slide callouts. Each record contains exact explanatory prose plus a
concrete SysML line prefix and optional occurrence number. Materialization
places the prose as a ``//`` comment immediately before that source element.
It never copies a PDF text layer, title, footer, page number, code echo, or
machine-generated explanation into a fixture. The local fixture tests verify
the source transcription, note content, and immediate semantic attachment.

No complete slide panel is an exact whitespace/typography-normalized duplicate
of the existing local PDF ledgers. Individual declarations and language
patterns naturally overlap with the formal SysML specification inventory; the
ledger does not claim semantic novelty for every statement.

Fixture policy
--------------

``fixture_candidate`` means that the visible panel is closed and does not use
an ellipsis or an external-language body. It does not promise parser support,
semantic resolution, or a standalone model: many examples reference types or
members introduced on another slide. The ``context_fragment`` flag and
``normalization_notes`` record those limits.

Slides 110 and 111 have three side-by-side source panels. Their ``code_blocks``
preserve the visual panel boundaries; ``code`` is their reading-order
concatenation. The original PDF is not a test-time dependency. If fixtures are
materialized later, copy only reviewed snippets into repository-owned test
data and keep independent AST expectations separate from the source text.

Known omissions and ambiguities
-------------------------------

* Slides 19, 26, 62, 64, and 66 show diagrams with code-like labels but no
  textual source panel; they are recorded as diagram-only observations.
* Slide 47 embeds Alf in an opaque action. The body is external language, not
  SysML textual notation.
* Slides containing ``...`` are intentionally incomplete/template excerpts,
  not closed fixtures.
* Slides 74, 76, 85, 129, 131, 133, 168, and 175 retain visible omissions,
  incomplete bodies, intentional calculation notation, typographic token
  variants, or selected-library context; their notes explain why they are not
  direct fixtures.
* The deck uses typographic single-quote glyphs for many quoted and operator
  names. All code excerpts normalize these consistently to ASCII apostrophes;
  this is a transcription normalization, not a claim that the printed glyphs
  are distinct SysML tokens.
* The PDF is a training presentation, not a normative AST or semantic-model
  specification. Do not use its rendered output as an AST golden.
