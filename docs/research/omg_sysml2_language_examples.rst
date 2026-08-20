OMG SysML 2.0 PDF Example Inventory
====================================

This is an evidence inventory for the official OMG ``SysML/2.0/Language/PDF``
document.  The machine-readable record is
``omg_sysml2_language_examples.json`` in this directory.  It is deliberately
kept separate from parser fixtures: a PDF code sample is not, by itself, an
independent AST expectation.

Source verification
-------------------

The source checked here is:

* OMG Systems Modeling Language (SysML) Version 2.0, Part 1: Language
  Specification, document ``formal/2026-03-02``.
* Official URL: ``https://www.omg.org/spec/SysML/2.0/Language/PDF``.
* The local copy has 691 physical pages and SHA-256
  ``46e6c0476a6f1f34f367d57e039d56659bff75e41d2e4b3d37ca4cadea84a83a``.
* ``curl -L -I`` returned HTTP 200 and ``content-length: 3804140`` on
  2026-08-19, matching the local PDF size.

Section 7 inventory status
--------------------------

Section 7 is printed pages 15--162 (physical pages 47--194).  PDF extraction
found 747 Courier-font blocks.  Of these, 379 contain a declaration and syntax
delimiters and are *candidate* textual examples, 59 are lexical/symbol
fragments, and 309 are fragments or graphical/table labels.  These are
evidence counts, not a claim that 379 independent fixtures exist.

The layout uses side-by-side graphical and textual notation, and examples are
often split over a page boundary.  Automatic extraction therefore cannot
reliably decide all fixture boundaries.  Human cleanup is required for:

* table-column interleaving and diagram labels;
* continuation blocks split across pages;
* ``...`` or prose placeholders that are not SysML source;
* examples relying on definitions introduced in another block; and
* ``rep``/``language`` bodies containing OCL, Alf, Python, or other external
  text.

The current checked-in release corpus contains 251 model files from the
``Systems-Modeling/SysML-v2-Release`` 2026-05 snapshot.  An exact-name scan
shows that it does **not** contain the PDF's named state examples
``Exercising``, ``Operating``, ``TurnedOn``, ``OperationalStates``,
``OnOff1``--``OnOff6``, ``PowerUp``, or ``TimeoutSignal``.  Thus a passing
251-file corpus run cannot establish coverage of all PDF examples, especially
section 7.18.

Section 7.18: states
--------------------

The following examples were manually transcribed from the printed text in
sections 7.18.1--7.18.4 and checked against the current parser.  ``pass`` means
syntax parsing and AST export currently succeed; it does **not** mean that a
complete hand-authored AST equality oracle is already present.

===============================  ==================  ================================
Inventory ID                     Printed page(s)    Current parser status
===============================  ==================  ================================
``s7-18-table17-*``               114--116           pass (table examples)
``s7-18-2-exercising``            117               pass
``s7-18-2-operating``             118               pass
``s7-18-2-turned-on``             118               pass
``s7-18-2-operational-states``    118--119           pass
``s7-18-2-vehicle-states-parallel`` 119             pass
``s7-18-3-onoff1``                119               pass
``s7-18-3-onoff2``                119--120           pass
``s7-18-3-onoff3``                120               pass
``s7-18-3-onoff4``                120--121           pass
``s7-18-3-onoff5``                121               pass
``s7-18-3-onoff6``                122               pass
``s7-18-4-vehicle-exhibit``      122               pass
``s7-18-4-vehicle-exhibit-shorthand`` 122           pass
===============================  ==================  ================================

The OnOff4 and OnOff5 forms exercise different, explicitly documented
compatibility boundaries. OnOff4 is the complete ``TransitionUsage``
guard-first form covered by the full-transition ordering overlay. OnOff5 is
the ``TargetTransitionUsage`` shorthand with the trigger before its guard;
that target form is accepted by the pinned upstream grammar and is not a
local grammar extension. OnOff5's closed transition effects are the separate
legacy semicolon compatibility case. OnOff6 exercises the corresponding
terminate action shorthand. OnOff4, OnOff5, and OnOff6 all parse successfully. Their
parser-derived snapshots are compared field-for-field by the official corpus
tests, while the handwritten state-oracle suite independently checks the
concrete fields for OnOff1--OnOff6. No target guard-first alternative is
accepted by this project.

Clauses 7.1--7.5: early language foundations
---------------------------------------------

The first manually reviewed ledger is
``manual_pdf_review/section_7_1_7_5.json``.  It covers every textual source
occurrence visually identified on printed pages 15--30 (physical pages
47--62), including repeated table cells and the two examples that cross a
printed-page boundary.  Clause 7.1 contains no textual source block; its
overview prose and lists are recorded as a scope result rather than invented
fixtures.  The companion human-readable review is
``manual_pdf_review/section_7_1_7_5.md``.

The merge manifest keeps two disjoint sets:

* ``entries`` contains only closed declarations or closed representative
  templates that are eligible for a repository-owned parser fixture;
* ``excluded_entries`` retains the verbatim reviewed source, page provenance,
  and an explicit reason whenever a block is lexical/contextual, incomplete,
  visibly mistyped, or incompatible with the current normative grammar.

The merged manual ledger currently has 422 reviewed textual records: 275
executable fixtures and 147 retained exclusions.  In particular, the formal
PDF's legacy ``action def setX(c : C, newX : Real)`` form is preserved as an
``official_compatibility_difference``.  The current official BNF, pilot
implementation, Spec42, sysmlpy, and copied release examples use body ``in``
parameter members, so the old form is not silently accepted by a grammar
overlay.  ``package Package 2`` is preserved as a visible source typo, and
the filtering example containing literal ``...`` is retained as incomplete.
These are evidence records, not positive conformance claims.

Evidence boundary
-----------------

The JSON record includes exact cleaned source for the state examples and the
source page/section.  The checked-in Section 7 goldens are span-free,
parser-derived snapshots of every AST dataclass field and are compared
field-for-field; a second parse of ``str(first.ast)`` additionally checks the
round-trip fixed point.  They are committed regression snapshots, not
independent semantic oracles.  Independent hand-authored AST oracles for the
state-machine examples live in ``test_official_ast_oracles.py`` and the
Section 8.4 semantic fixtures have their own field-level oracles.

The raw extraction used for the whole section is retained in
``omg_sysml2_language_section7_blocks.json``.  It contains the physical page,
printed page, visual top coordinate, extracted lines, and rough classification
for every one of the 747 blocks.  It is an evidence ledger, not a fixture
directory: unreviewed OCR/layout fragments are intentionally not fed to the
parser as tests.  The smaller ``omg_sysml2_language_examples.json`` file is
the durable, reviewed summary and contains manually cleaned state examples.

Annex A currently has one additional visually reviewed closed source panel:
the complete ``part def Vehicle`` block from printed page 637 (physical page
669), recorded in ``manual_pdf_review/annex_a_3_vehicle_definition.json`` and
checked by an independent field-level oracle.  The remaining Annex A panels
and later semantic examples are tracked as open coverage work rather than
being represented by parser-derived claims.

Status vocabulary
-----------------

``manually_transcribed_from_pdf``
    A human normalized the relevant Courier text while retaining the printed
    page and clause reference.

``candidate_text_code``
    A block found by the extraction heuristic that needs manual review before
    becoming a test fixture.

``lexical_or_fragment`` / ``fragment_or_graphical``
    Code-like PDF content that is not an independently parseable model by
    itself (for example a keyword legend, multiplicity, diagram label, or an
    omitted ``...`` compartment).

``independent_ast_expected_value_still_required``
    The source has been identified, but the expected AST must be written and
    reviewed separately from the parser's own output.
