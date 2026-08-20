## Review conclusion

This is an update to our existing PR #10 review comment only. The PR #10 body is unchanged; the cumulative evidence and remaining findings belong to PR #11.

The precedence reversal in PR #10 is technically correct for the generated ANTLR grammar and agrees with OMG KerML Table 6. The upstream generator emits the KEBNF alternatives from low to high precedence, but ANTLR direct-left-recursive alternatives must be emitted from high to low precedence. With the reversal, `a + b * c` parses as `a + (b * c)`, and exponentiation remains right-associative: `a ** b ** c` parses as `a ** (b ** c)`.

| Issue | Example | OMG/KEBNF | Direct official Pilot | PR #10 conclusion | Follow-up in PR #11 |
|---|---|---|---|---|---|
| Precedence order | `a + b * c` | Additive below multiplicative | Accepts with `+` outer and `*` nested | Correct after reversal | Preserved |
| Exponentiation associativity | `a ** b ** c` | Right-associative exception to KEBNF Note 2 | Accepts right-nested | Correct | Preserved |
| Same-tier associativity | `a + b - c`; `a and b or c` | Left-associative | Direct probes agree for supported forms | Correct | Regression coverage expanded |
| Range placement | `a .. b + c` | Range between additive and relational | Representative form accepted | Correct tier | PR #11 keeps normative range behavior even where Pilot rejects repeated `..` |
| Classification/metaclassification continuations | `a istype T + b`; `a as T + b`; `a @@ T + b`; `a meta T + b` | KEBNF recursively derives these through `OwnedExpression` operands; it does not establish a rejection boundary here | Rejects | This is outside PR #10's precedence conclusion; PR #11 preserves the Pilot boundary and discloses the KEBNF/Pilot gap | Disclosed in PR #11 |
| Primary boundary | `a[]`; `a#()`; `a(b)(c)` | Empty sequences and unconstrained repeated invocation are not listed primary forms | Rejects | PR #10 accepted some of these | PR #11 rejects them with explicit primary/sequence rules |

Normative references: [OMG Table 6](https://www.omg.org/spec/KerML/1.0/PDF#page=124), [KEBNF precedence note](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1061-L1064), and [official Pilot expression tiers](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext#L53-L295).

The classification and metaclassification cases need one qualification. In the official KEBNF, `BinaryOperatorExpression` operands recursively reach `OwnedExpression`, while `ClassificationExpression` and `MetaclassificationExpression` are themselves `OwnedExpression` alternatives. The examples are therefore derivable in the declarative KEBNF; the KEBNF does not establish a rejection boundary here. The direct official Pilot rejects them, and PR #11 now records this as E4, a disclosed KEBNF/Pilot acceptance gap. Evidence: [OwnedExpression and binary operators](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L932-L962), [classification and metaclassification](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L979-L1001), and [argument operands](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1003-L1010).

## Boundary that belongs to PR #11

The precedence fix is not by itself a complete acceptance-set fix. PR #11 carries the remaining expression and body boundaries in [commit `16951ec8466e95c6ab582c9c09889edf611d0a56`](https://github.com/HansBug/sysml-v2-grammar/commit/16951ec8466e95c6ab582c9c09889edf611d0a56).

| Issue | Examples | Normative / official result | Current PR #11 result |
|---|---|---|---|
| E4: classification/metaclassification continuation | `a istype T + b`; `a as T + b`; `a @@ T + b`; `a meta T + b` | KEBNF recursively derives through `OwnedExpression` operands; direct Pilot rejects | PR #11 rejects and discloses the KEBNF/Pilot gap |
| R1: recursive conditional operands | `a + if b ? c else d`; `-if b ? c else d`; `a ** if b ? c else d`; `a ?? if b ? c else d` | The KEBNF derives these through recursive `OwnedExpression` operands; the released Pilot rejects all four | Fix 57's paired normal/conditional layers accept all four with zero exact ambiguity; the direct Pilot remains narrower and the discrepancy is disclosed in PR #11 |
| R1: conditional condition boundary | `if if a ? b else c ? d else e` | The released Pilot rejects this direct condition form (`syntaxErrors=true`, `parserErrors=1`) | Current ANTLR accepts it to EOF under its deterministic recursive rule; PR #11 discloses this Pilot-narrower delta and does not claim equivalence |
| R2a: valid nested result body | `a.{;}`; `a.{x;;}`; `a.{x; ;}`; `a.{x ; ;}`; `a.{y ; ;}` | Direct Pilot accepts these as a final nested result, not as a bare action item | Fix 53 changes `defaultReferenceUsage` to require `usageDeclaration usageCompletion`; all five are accepted with zero exact ambiguity |
| R2b: malformed separator placement | `a.{;;}`; `a.{; x}`; `a.{x;; y}`; `a.{x;;; y}`; `a.{x; ; y}` | Direct Pilot rejects all five; `CalculationBodyItem` has no bare-semicolon item | Fix 53 rejects all five with EOF/diagnostics |
| R3: SysML expression-body scope | `a.{ x }`; `a.{ private attribute x := y; x }` | SysML KEBNF and the official Pilot override expression bodies with `CalculationBody` | PR #11 uses `calculationBodyPart`, preserving the body/result boundary without exact ambiguity |
| R4: comment/note boundary | `a.{/* c */}`; `(/* c */)`; newline-delimited `//*` | Direct Pilot accepts model-owned regular comments in body positions, hides multiline notes, and rejects comments as expressions | Fixes 54/55 keep `REGULAR_COMMENT` visible, `ML_NOTE` hidden, and remove comments from `baseExpression` |
| R6: contextual names | `typed`; `language`; `locale`; `crosses` | Direct Pilot accepts `typed` and rejects the three literal keywords at `OwnedExpression` | Fix 56 adds `TYPED` to the contextual-name alternative and rejects the three over-broad keyword cases |
| R5: release revision persistence | Watcher update path | A release tag is not an immutable source revision | PR #11 pins the default revision, but the watcher follow-up remains open |

R2 source evidence: [SysML `CalculationBody`](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf#L1363-L1378), [KEBNF `Usage`](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf#L309-L319), [Pilot `DefaultReferenceUsage`](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L632-L635), and [the generated Fix 53 patch](https://github.com/HansBug/sysml-v2-grammar/blob/16951ec8466e95c6ab582c9c09889edf611d0a56/scripts/generate_grammar.py#L2328-L2341).

Additional evidence: [SysML/Pilot calculation-body override](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L2436-L2439), [current comment/note lexer](https://github.com/HansBug/sysml-v2-grammar/blob/16951ec8466e95c6ab582c9c09889edf611d0a56/grammar/SysMLv2Lexer.g4#L248-L265), [current contextual-name rules](https://github.com/HansBug/sysml-v2-grammar/blob/16951ec8466e95c6ab582c9c09889edf611d0a56/grammar/SysMLv2Parser.g4#L306-L323), and [Fixes 54-57](https://github.com/HansBug/sysml-v2-grammar/blob/16951ec8466e95c6ab582c9c09889edf611d0a56/scripts/generate_grammar.py#L2354-L2410).

## Direct first-party runtime evidence

The official `.kebnf` assets are declarative and have no executable interpreter. The separate direct-run evidence used the official Pilot lexer/parser/runtime, not a KEBNF-to-ANTLR conversion:

| Run | Result |
|---|---|
| Official Pilot fixture syntax path | `251/251` official fixture files accepted with official diagnostics and EOF checks |
| Official Pilot R1 matrix | `76/136` accepted and `60/136` rejected; rejected examples include `a + if b ? c else d`, `-if b ? c else d`, `a ** if b ? c else d`, `a ?? if b ? c else d`, `a .. b .. c`, recursive unary forms, and `if if a ? b else c ? d else e` |
| Official Pilot classification/metaclassification probes | Rejects `a istype T + b`, `a as T + b`, `a @@ T + b`, and `a meta T + b` | E4 is a disclosed KEBNF/Pilot boundary; PR #11 preserves the direct Pilot result |
| Official full runtime smoke test | 94 library files loaded; `package P { calc c { 1 + 2 * 3 } }` parsed successfully without `ERROR:` output |

The locally rebuilt runtime artifact and first-party source revisions are pinned in the [PR #11 evidence table](https://github.com/daltskin/sysml-v2-grammar/pull/11), including SHA-256 values for the rebuilt official Pilot runtime and Xtext sources. The syntax-only harness replaces only isolated semantic model construction with no-op dynamic objects; the official lexer, parser, token stream, lookahead, and EOF behavior remain official.

## Final scope

PR #10's precedence correction is supported and should be evaluated on that basis. The residual acceptance, body, classification, and release-management findings are tracked in PR #11, whose body now provides the complete OMG/KEBNF/Pilot evidence matrix. This is an update to this existing PR #10 comment only; the PR #10 body is unchanged.
