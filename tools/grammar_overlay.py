"""Apply and record the project's narrow SysML grammar compatibility overlay.

The pinned ``daltskin/sysml-v2-grammar`` submodule is the sole source of the
base G4 files.  This module applies only the reviewed SysML v2 state-machine
compatibility transformations required by the OMG SysML 2.0 Language examples
after the G4 files have been copied into the generated directory.  The overlay
does not alter ``targetTransitionUsage``: its trigger-before-guard and
guard-only alternatives remain the upstream grammar.  KerML-only grammar
extensions are intentionally outside this package and are not added here.

No generated file is edited by hand.  The command writes
``grammar-provenance.json`` beside the generated artifacts with the actual
submodule revision, describe value, input hash, overlay identifier, and output
hash.  A future upstream revision that changes any rule being overlaid fails
loudly instead of silently receiving an unsafe text substitution.

.. list-table:: Grammar overlay roadmap
   :header-rows: 1

   * - Symbol
     - Responsibility
   * - :func:`apply_overlay`
     - Validate and apply the reviewed SysML v2 compatibility
       transformations exactly once.
   * - :func:`write_manifest`
     - Persist machine-readable upstream and effective-grammar provenance.
   * - :func:`main`
     - Provide the Makefile-facing command-line entry point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

OVERLAY_IDENTIFIER = "pysysmlv2-sysml-state-v1"
MANIFEST_SCHEMA_VERSION = 1

# These notes are emitted into ``grammar-provenance.json`` and are deliberately
# kept beside the exact replacements below.  The copied G4 is generated output;
# this table is the review record for every local delta from the pinned upstream
# grammar.  ``official_example`` means that a closed example in the OMG release
# or formal language PDF was checked by hand.  ``upstream_gap`` means that the
# generated ANTLR grammar is narrower than the normative notation, not that the
# OMG example should be changed.
OVERLAY_NOTES = (
    {
        "id": "transition-trigger-guard-order",
        "rules": ["transitionUsage"],
        "classification": "upstream_gap",
        "official_evidence": "OMG SysML 2.0 Language formal PDF, Clause 7.18.3 (State Examples), printed pages 120-121: complete TransitionUsage in OnOff3 uses trigger-before-guard and complete TransitionUsage in OnOff4 uses guard-before-trigger (https://www.omg.org/spec/SysML/2.0/Language/PDF). The official Pilot's corresponding rule is https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L1866-L1882.",
        "reason": "The generated full TransitionUsage rule hard-codes trigger-before-guard, although the normative full-transition examples exercise both orders.",
    },
    {
        "id": "transition-effect-semicolon",
        "rules": [
            "transitionPerformActionUsage",
            "transitionAcceptActionUsage",
            "transitionSendActionUsage",
            "transitionAssignmentActionUsage",
        ],
        "classification": "upstream_gap",
        "official_evidence": "OMG SysML 2.0 Language formal PDF, Clause 7.18.3 (State Examples), printed page 121, OnOff5 contains closed transition effects ``do action powerUp : PowerUp; then`` and ``do send new TimeoutSignal() via commPort; then`` (https://www.omg.org/spec/SysML/2.0/Language/PDF).",
        "reason": "The shorthand effect form is a closed action terminated by ``;``; the generated rules only allow a brace body or an omitted body.",
    },
    {
        "id": "terminate-action-shorthand",
        "rules": ["actionUsage"],
        "classification": "upstream_gap",
        "official_evidence": "OMG SysML 2.0 Language formal PDF, Clause 7.17.10 (Terminate Usages) and Clause 7.18.3 (State Examples), printed page 122 OnOff6: ``action stop terminate;`` (https://www.omg.org/spec/SysML/2.0/Language/PDF).",
        "reason": "The generated actionUsage requires actionBody after the declaration and rejects the official terminate shorthand.",
    },
)

_TRANSITION_USAGE_BEFORE = """transitionUsage
    : TRANSITION ( usageDeclaration? FIRST )? featureChainMember emptyParameterMember ( emptyParameterMember triggerActionMember )? ( guardExpressionMember )? ( effectBehaviorMember )? THEN transitionSuccessionMember actionBody
    ;"""
_TRANSITION_USAGE_AFTER = """transitionUsage
    : TRANSITION ( usageDeclaration? FIRST )? featureChainMember emptyParameterMember
      (
          // [pysysmlv2 overlay: transition-trigger-guard-order]
          // Difference from pinned upstream ANTLR rule: upstream fixes this
          // optional group to ``emptyParameterMember triggerActionMember``
          // before ``guardExpressionMember``.
          // Upstream source: https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1767-L1769
          // OMG SysML 2.0 Language, Clause 7.18.3, printed pages 120-121:
          // OnOff3 uses ``accept ... if ...`` while OnOff4 uses
          // ``if ... accept ...``. These are both complete TransitionUsage
          // forms; OnOff5 is a separate target-transition shorthand and is
          // intentionally not evidence for this alternative. The PDF is the
          // official source:
          // https://www.omg.org/spec/SysML/2.0/Language/PDF
          // Keep both orders because the upstream KEBNF converter emits only
          // the former and would reject the latter official examples.
          emptyParameterMember triggerActionMember ( guardExpressionMember )?
        | guardExpressionMember ( emptyParameterMember triggerActionMember )?
      )?
      ( effectBehaviorMember )? THEN transitionSuccessionMember actionBody
    ;"""
_TRANSITION_PERFORM_ACTION_USAGE_BEFORE = """transitionPerformActionUsage
    : performActionUsageDeclaration ( LBRACE actionBodyItem* RBRACE )?
    ;"""
_TRANSITION_PERFORM_ACTION_USAGE_AFTER = """transitionPerformActionUsage
    // [pysysmlv2 overlay: transition-effect-semicolon]
    // Difference from pinned upstream ANTLR rule: upstream allows a braced
    // body or omission only; this alternative admits the closed ``SEMI`` form.
    // Upstream source: https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1799-L1801
    // OMG SysML 2.0 Language Clause 7.18.3, printed page 121, OnOff5 shows
    // ``do action powerUp : PowerUp; then``:
    // https://www.omg.org/spec/SysML/2.0/Language/PDF
    : performActionUsageDeclaration ( LBRACE actionBodyItem* RBRACE | SEMI )?
    ;"""
_TRANSITION_ACCEPT_ACTION_USAGE_BEFORE = """transitionAcceptActionUsage
    : acceptNodeDeclaration ( LBRACE actionBodyItem* RBRACE )?
    ;"""
_TRANSITION_ACCEPT_ACTION_USAGE_AFTER = """transitionAcceptActionUsage
    // [pysysmlv2 overlay: transition-effect-semicolon]
    // Difference from pinned upstream ANTLR rule: admit the same closed
    // ``SEMI`` effect alternative as the official OnOff5 notation.
    // Upstream source: https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1803-L1805
    // OMG SysML 2.0 Language Clause 7.18.3, printed page 121:
    // https://www.omg.org/spec/SysML/2.0/Language/PDF
    : acceptNodeDeclaration ( LBRACE actionBodyItem* RBRACE | SEMI )?
    ;"""
_TRANSITION_SEND_ACTION_USAGE_BEFORE = """transitionSendActionUsage
    : sendNodeDeclaration ( LBRACE actionBodyItem* RBRACE )?
    ;"""
_TRANSITION_SEND_ACTION_USAGE_AFTER = """transitionSendActionUsage
    // [pysysmlv2 overlay: transition-effect-semicolon]
    // Difference from pinned upstream ANTLR rule: admit the closed ``SEMI``
    // effect alternative. OMG SysML 2.0 Language Clause 7.18.3, printed page
    // 121, OnOff5 shows
    // ``do send new TimeoutSignal() via commPort; then``.
    // Upstream source: https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1807-L1809
    // https://www.omg.org/spec/SysML/2.0/Language/PDF
    : sendNodeDeclaration ( LBRACE actionBodyItem* RBRACE | SEMI )?
    ;"""
_TRANSITION_ASSIGNMENT_ACTION_USAGE_BEFORE = """transitionAssignmentActionUsage
    : assignmentNodeDeclaration ( LBRACE actionBodyItem* RBRACE )?
    ;"""
_TRANSITION_ASSIGNMENT_ACTION_USAGE_AFTER = """transitionAssignmentActionUsage
    // [pysysmlv2 overlay: transition-effect-semicolon]
    // Difference from pinned upstream ANTLR rule: apply the same closed-effect
    // ``SEMI`` alternative to assignment effects, keeping all four
    // EffectBehaviorUsage alternatives consistent. Upstream source:
    // https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1811-L1813
    // The official closed-effect notation is documented in SysML 2.0
    // Language Clause 7.18.3, printed page 121:
    // https://www.omg.org/spec/SysML/2.0/Language/PDF
    : assignmentNodeDeclaration ( LBRACE actionBodyItem* RBRACE | SEMI )?
    ;"""
_ACTION_USAGE_BEFORE = """actionUsage
    : occurrenceUsagePrefix ACTION actionUsageDeclaration actionBody
    ;"""
_ACTION_USAGE_AFTER = """actionUsage
    : occurrenceUsagePrefix ACTION actionUsageDeclaration actionBody
    // [pysysmlv2 overlay: terminate-action-shorthand]
    // Difference from pinned upstream ANTLR rule: upstream requires an
    // ``actionBody`` after ``actionUsageDeclaration``. The added alternative
    // represents the declaration-only terminate usage and its terminating
    // semicolon. Upstream source:
    // https://github.com/daltskin/sysml-v2-grammar/blob/v2026.05.0/grammar/SysMLv2Parser.g4#L1487-L1489
    // OMG SysML 2.0 Language formal PDF, Clause 7.17.10 (Terminate Usages)
    // and Clause 7.18.3 (State Examples), printed page 122 (OnOff6), explicitly
    // uses ``action stop terminate;``:
    // https://www.omg.org/spec/SysML/2.0/Language/PDF
    | occurrenceUsagePrefix ACTION actionUsageDeclaration TERMINATE SEMI
    ;"""
_TRANSFORMATIONS = (
    (
        "transition trigger and guard ordering",
        _TRANSITION_USAGE_BEFORE,
        _TRANSITION_USAGE_AFTER,
    ),
    (
        "transition perform-effect semicolon",
        _TRANSITION_PERFORM_ACTION_USAGE_BEFORE,
        _TRANSITION_PERFORM_ACTION_USAGE_AFTER,
    ),
    (
        "transition accept-effect semicolon",
        _TRANSITION_ACCEPT_ACTION_USAGE_BEFORE,
        _TRANSITION_ACCEPT_ACTION_USAGE_AFTER,
    ),
    (
        "transition send-effect semicolon",
        _TRANSITION_SEND_ACTION_USAGE_BEFORE,
        _TRANSITION_SEND_ACTION_USAGE_AFTER,
    ),
    (
        "transition assignment-effect semicolon",
        _TRANSITION_ASSIGNMENT_ACTION_USAGE_BEFORE,
        _TRANSITION_ASSIGNMENT_ACTION_USAGE_AFTER,
    ),
    (
        "terminate action usage shorthand",
        _ACTION_USAGE_BEFORE,
        _ACTION_USAGE_AFTER,
    ),
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file's exact bytes.

    :param path: File whose bytes are to be hashed.
    :type path: pathlib.Path
    :return: Lowercase hexadecimal SHA-256 digest.
    :rtype: str

    Example::

        >>> len(sha256_file(Path(__file__)))
        64
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_overlay(parser_grammar: Path) -> bool:
    """Apply the version-guarded SysML v2 compatibility overlay to a copied G4 file.

    The operation is idempotent for the exact effective grammar emitted by this
    module.  Any other form is rejected because it means that an upstream
    grammar update requires a deliberate compatibility review.

    :param parser_grammar: Copied ``SysMLv2Parser.g4`` file in the generated
        directory.
    :type parser_grammar: pathlib.Path
    :return: Whether this invocation changed the file.
    :rtype: bool
    :raises ValueError: If a required source rule is missing, duplicated, or
        already transformed to an unknown form.

    Example::

        >>> path = Path("/tmp/pysysmlv2-overlay-example.g4")
        >>> source = "\\n\\n".join(before for _, before, _ in _TRANSFORMATIONS)
        >>> _ = path.write_text(source)
        >>> apply_overlay(path)
        True
        >>> "transition-trigger-guard-order" in path.read_text()
        True
        >>> path.unlink()
    """
    source = parser_grammar.read_text(encoding="utf-8")
    changed = False
    for rule_name, before, after in _TRANSFORMATIONS:
        before_count = source.count(before)
        after_count = source.count(after)
        if before_count == 1 and after_count == 0:
            source = source.replace(before, after, 1)
            changed = True
            continue
        if before_count == 0 and after_count == 1:
            continue
        raise ValueError(
            "Cannot apply {} overlay: expected one unmodified or one effective {} rule, "
            "found {} and {}.".format(OVERLAY_IDENTIFIER, rule_name, before_count, after_count)
        )
    if changed:
        parser_grammar.write_text(source, encoding="utf-8")
    return changed


def build_manifest(
    upstream_revision: str,
    upstream_describe: str,
    upstream_parser_sha256: str,
    effective_parser_sha256: str,
) -> Dict[str, object]:
    """Build stable generated-grammar provenance data.

    :param upstream_revision: Exact pinned grammar submodule commit.
    :type upstream_revision: str
    :param upstream_describe: Human-readable git describe value for that
        commit.
    :type upstream_describe: str
    :param upstream_parser_sha256: Hash before applying this project's overlay.
    :type upstream_parser_sha256: str
    :param effective_parser_sha256: Hash after applying the overlay.
    :type effective_parser_sha256: str
    :return: JSON-serializable provenance mapping.
    :rtype: dict[str, object]

    Example::

        >>> build_manifest("abc", "v0", "1" * 64, "2" * 64)["overlay"]
        'pysysmlv2-sysml-state-v1'
    """
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "upstream": {
            "revision": upstream_revision,
            "describe": upstream_describe,
            "parser_sha256": upstream_parser_sha256,
        },
        "overlay": OVERLAY_IDENTIFIER,
        "overlay_notes": list(OVERLAY_NOTES),
        "effective_parser_sha256": effective_parser_sha256,
    }


def _git_value(upstream_grammar_dir: Path, arguments: Tuple[str, ...]) -> str:
    """Read one stable git value from the pinned grammar checkout.

    :param upstream_grammar_dir: ``grammar/`` directory within the submodule.
    :type upstream_grammar_dir: pathlib.Path
    :param arguments: Arguments after ``git``.
    :type arguments: tuple[str, ...]
    :return: Trimmed command output.
    :rtype: str
    :raises RuntimeError: If the pinned grammar directory is not a usable git
        checkout.
    """
    try:
        output = subprocess.check_output(
            ("git", "-C", str(upstream_grammar_dir.parent), *arguments),
            stderr=subprocess.STDOUT,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Cannot determine pinned grammar provenance") from error
    return output.strip()


def write_manifest(
    manifest_path: Path,
    upstream_grammar_dir: Path,
    upstream_parser_sha256: str,
    effective_parser_sha256: str,
) -> None:
    """Write exact upstream and effective grammar provenance as JSON.

    :param manifest_path: Destination ``grammar-provenance.json`` path.
    :type manifest_path: pathlib.Path
    :param upstream_grammar_dir: Pinned submodule ``grammar/`` directory.
    :type upstream_grammar_dir: pathlib.Path
    :param upstream_parser_sha256: Hash of the copied upstream parser G4.
    :type upstream_parser_sha256: str
    :param effective_parser_sha256: Hash after applying the overlay.
    :type effective_parser_sha256: str
    :return: ``None`` after deterministic JSON is written.
    :rtype: None

    Example::

        This function is invoked by ``make antlr_update`` after copying the
        pinned grammar submodule.
    """
    manifest = build_manifest(
        _git_value(upstream_grammar_dir, ("rev-parse", "HEAD")),
        _git_value(upstream_grammar_dir, ("describe", "--tags", "--always")),
        upstream_parser_sha256,
        effective_parser_sha256,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Apply the grammar overlay and write its generated provenance manifest.

    :param arguments: Optional command-line arguments, defaults to ``None``.
    :type arguments: sequence[str], optional
    :return: Zero after the effective grammar and manifest have been written.
    :rtype: int
    :raises ValueError: If the copied parser grammar differs from the reviewed
        upstream form.

    Example::

        $ python -m tools.grammar_overlay --help
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parser_grammar", type=Path)
    parser.add_argument("upstream_grammar_dir", type=Path)
    parser.add_argument("manifest", type=Path)
    options = parser.parse_args(arguments)
    upstream_hash = sha256_file(options.parser_grammar)
    apply_overlay(options.parser_grammar)
    write_manifest(
        options.manifest,
        options.upstream_grammar_dir,
        upstream_hash,
        sha256_file(options.parser_grammar),
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
