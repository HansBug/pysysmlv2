## Scope and review status

This is the cumulative follow-up to [PR #10](https://github.com/daltskin/sysml-v2-grammar/pull/10). It preserves the precedence correction from #10 and adds the expression-boundary, body, lexical, contextual-name, generator, and reproducibility work required for a defensible review of the generated ANTLR grammar.

**Review status: REQUEST CHANGES for strict normative acceptance-set alignment.** The precedence grouping is supported by OMG Table 6, the first-party KEBNF, and direct execution of the official Pilot parser. The current grammar now matches the released Pilot for the fixed R2, R4, and R6 boundaries, but the exhaustive R1 matrix still contains 59 KEBNF-derivable forms rejected by both implementations and one ANTLR-only form; this PR must not claim full KEBNF/Pilot acceptance-set equivalence.

The final cumulative head is [`b3f52b38`](https://github.com/HansBug/sysml-v2-grammar/commit/b3f52b388456d818a559bfd5b772374482006f3e), `fix: regenerate lexer token vocabulary`. This update changes the PR #11 body only. The PR #10 body is deliberately unchanged; only the existing [PR #10 review comment](https://github.com/daltskin/sysml-v2-grammar/pull/10#issuecomment-5351833338) is maintained separately.

## First-party evidence sources

| ID | First-party asset | Revision or hash | Evidence role |
|---|---|---|---|
| N | [OMG KerML 1.0, Clause 8.2.5.8.1, Table 6](https://www.omg.org/spec/KerML/1.0/PDF#page=124) | OMG specification | Normative precedence tiers and associativity |
| K | [KerML KEBNF lexical and expression source](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf) | Release commit `de1070ae8e79c21532b8004fc663d47b35d0e9fa`; SHA-256 `2df526a1d36fc08a24adc05094fca069c3bef51aeb688f8328d408eee17103f8` | Declarative KerML lexical, expression, and body productions |
| S | [SysML KEBNF body source](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf) | Same release commit; SHA-256 `b30e3af5ab0092ac9528ea714822412c7fe2467dff6983215eb9ac5e65139ed3` | Declarative SysML `CalculationBody` productions |
| P | [Official Pilot KerML expression grammar](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext) | Pilot commit `fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa`; SHA-256 `499ec9b99d6c0a9195894fd420e168343fa1906698c4d1ac9ca3c0a94ca00cc7` | First-party executable expression grammar |
| X | [Official Pilot SysML grammar](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext) | Same Pilot commit; SHA-256 `8d3185ca84bcfd3d6a2c3c2c5d93d6cbdbc3610789c0434d45f8ba46a0675266` | First-party `CalculationBody` and `ExpressionBody` override |
| R | Official Pilot runtime `jupyter-sysml-kernel-0.60.1-all.jar` | SHA-256 `f1e1880b337ed3c50bc65c32599f43ec9148cc4ca47ef91a99c5022ec677d9ac` | Direct lexer/parser/runtime execution |
| A | [ANTLR 4.13.2 tool](https://www.antlr.org/download/antlr-4.13.2-complete.jar) | SHA-256 `eae2dfa119a64327444672aff63e9ec35a20180dc5b8090b7a6ab85125df4d76` | Independent rebuild of this repository's generated grammar |

The official `.kebnf` files are declarative assets. The pinned release archive contains no official KEBNF interpreter, so KEBNF evidence below is direct source inspection plus an independent fixed-point derivability check over the cited productions; it is not an execution of a KEBNF-to-ANTLR conversion. The direct-runtime tables use the official Pilot `InternalSysMLLexer`, `InternalSysMLParser`, `XtextTokenStream`, grammar access, and official runtime JAR. The ANTLR results are reported as a separate implementation under test. No Pilot result is presented as a normative KEBNF result.

## Cumulative file-to-evidence map

Every file changed by this PR is listed below. All repository links point to the immutable final PR head.

| Changed file | Cumulative change | Evidence |
|---|---|---|
| [`Makefile`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/Makefile) | Compiles the split lexer/parser with grammar name `SysMLv2`, checks parser status and diagnostics, and runs the conformance gate. | [Test targets](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/Makefile#L49-L81) |
| [`grammar/SysMLv2Lexer.g4`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Lexer.g4) | Regenerated lexer with distinct visible `REGULAR_COMMENT`, hidden `ML_NOTE`, EOF-qualified line-note behavior, and the generated keyword vocabulary. | [Comment terminals](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Lexer.g4#L248-L265) |
| [`grammar/SysMLv2Lexer.tokens`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Lexer.tokens) | Regenerated token vocabulary for the cumulative grammar and contextual-name changes. | [Token artifact](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Lexer.tokens) |
| [`grammar/SysMLv2Parser.g4`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4) | Adds explicit precedence layers, primary/body boundaries, classification/metaclassification boundaries, SysML calculation-body behavior, Fix 53, and Fix 55/56 parser changes. | [Expression rules](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L20-L177), [name rules](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L219-L245), [usage boundary](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L1135-L1154), [calculation body](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L1929-L1945) |
| [`scripts/ExpressionGrammarTest.java`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java) | Adds exact-ambiguity, EOF, precedence, associativity, classification, primary, body, root, R1, R2, R4, and R6 regression cases. | [Regression corpus](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java#L190-L285) |
| [`scripts/config.json`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/config.json) | Pins OMG release `2026-05`, immutable release revision `de1070ae8e79c21532b8004fc663d47b35d0e9fa`, grammar version `2026.05.2`, official KEBNF paths, and generated grammar names. | [Pinned configuration](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/config.json#L1-L18) |
| [`scripts/conformance.py`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/conformance.py) | Pins fixture retrieval, stamps grammar/tool inputs before class reuse, rejects parser non-zero exits/stderr, and rejects empty required suites. | [Build stamp and parser invocation](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/conformance.py#L103-L191), [suite guard](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/conformance.py#L194-L211) |
| [`scripts/generate_grammar.py`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/generate_grammar.py) | Emits explicit expression layers, applies Fix 51, removes 43 unreachable rules in Fix 52, applies Fix 53, and records Fix 54/55/56 plus superseded Fix 42/50. | [Patch ledger](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/generate_grammar.py#L2214-L2397); [Expression emission](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/generate_grammar.py#L2449-L2612) |
| [`grammar/PATCHES.md`](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/PATCHES.md) | Records Fix 51, Fix 52 (43 unreachable parser rules removed), Fix 53, superseded Fix 42/50, and applied Fix 54/55/56. | [Patch ledger](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/PATCHES.md#L423-L452) |

## Normative precedence correction

[OMG Table 6](https://www.omg.org/spec/KerML/1.0/PDF#page=124) places conditional expressions below the binary tiers. [KEBNF Note 2](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1061-L1064) makes precedence implicit and specifies left associativity for binary operators except exponentiation. ANTLR direct-left-recursive alternatives therefore have to be emitted high-to-low, while the upstream KEBNF generator writes the source alternatives low-to-high.

| Finding | Example | OMG/KEBNF expectation | Direct official Pilot | Current PR #11 | Evidence mapping |
|---|---|---|---|---|---|
| E1: additive versus multiplicative | `a + b * c` | `a + (b * c)` | Accepts the corresponding precedence | Accepts with additive outer and multiplicative inner layers | [Table 6](https://www.omg.org/spec/KerML/1.0/PDF#page=124); [ANTLR layers](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L72-L90) |
| E1: exponentiation associativity | `a ** b ** c` | `a ** (b ** c)` | Accepts right-nested exponentiation | Right-recursive exponentiation produces the same grouping | [KEBNF Note 2](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1061-L1064); [exponentiation rule](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L84-L90) |
| E2: synonym tiers | `a | b or c`; `a & b and c` | `|` shares the `or` tier; `&` shares the `and` tier | Direct probes accept the tier combinations | Explicit same-tier ANTLR alternatives preserve them | [KEBNF operators](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L949-L969); [Pilot tiers](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext#L101-L144) |
| E3: range tier | `a .. b + c` | Range is below additive and above relational | Representative range expressions accepted | `rangeExpression` is between additive and relational; repeated range remains normative-left-associative | [Table 6](https://www.omg.org/spec/KerML/1.0/PDF#page=124); [range rule](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L72-L82) |
| E4: classification and metaclassification continuations | `a istype T + b`; `a istype T < b`; `a hastype T + b`; `a @ T + b`; `a as T + b`; `a as T < b`; `a @@ T + b`; `a @@ T < b`; `a meta T + b`; `a meta T < b` | KEBNF recursively derives these through binary-operator operands that reach `OwnedExpression`; it does not state a rejection boundary here | Direct Pilot rejects these probes | Current PR #11 rejects them; this is a disclosed KEBNF/Pilot acceptance gap, not a normative KEBNF rejection | [KEBNF expression/classification productions](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L932-L1010); [classification rule](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L61-L70) |
| E5: primary boundaries | `a[]`; `a#()`; `a(b)(c)` | Empty sequence/index forms and unconstrained repeated invocation are outside the listed primary forms | Rejects | Rejects with EOF/diagnostics | [KEBNF primary forms](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1068-L1178); [primary rule](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L104-L120) |

## R2: calculation-body separator boundary fixed

The official SysML [CalculationBody](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf#L1363-L1378) is `CalculationBodyItem*` followed by at most one `ResultExpressionMember`. A bare semicolon is not an action item, but `OwnedExpression` can recursively contain a nested body expression. The official Pilot [DefaultReferenceUsage](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L632-L635) also requires a declaration.

Fix 53 keeps the broader anonymous-usage compatibility rule where it is needed, but restores `defaultReferenceUsage` to `usageDeclaration usageCompletion`. This removes the competing anonymous action-item path and makes the result-body tree deterministic.

| Finding | Example | Official Pilot direct run | Current PR #11 | Evidence mapping |
|---|---|---|---|---|
| R2a: empty nested result | `a.{;}` | Accepts as `ResultExpressionMember -> OwnedExpression -> BodyExpression` | Accepts; exact ambiguity count `0` | [CalculationBody](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf#L1363-L1378); [Fix 53](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/generate_grammar.py#L2339-L2352) |
| R2a: item plus result | `a.{x;;}` | Accepts `x;` item followed by a nested `;` result | Accepts; exact ambiguity count `0` | [Regression cases](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java#L220-L227) |
| R2a: spaced result forms | `a.{x; ;}`; `a.{x ; ;}`; `a.{y ; ;}` | Accepts all three | Accepts all three; exact ambiguity count `0` | [Regression cases](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java#L220-L227) |
| R2b: repeated separator | `a.{;;}` | Rejects | Rejects with EOF/diagnostics | [Invalid cases](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java#L275-L283) |
| R2b: separator before item | `a.{; x}` | Rejects; no bare-semicolon action item | Rejects | [Usage boundary](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/grammar/SysMLv2Parser.g4#L1135-L1154) |
| R2b: item after result | `a.{x;; y}`; `a.{x;;; y}`; `a.{x; ; y}` | Rejects all three | Rejects all three | [Invalid cases](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/ExpressionGrammarTest.java#L275-L283) |

## R3: SysML body scope is explicit

The generic KerML [ExpressionBody](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1253-L1260) is defined through `FunctionBodyPart`. The SysML release defines [CalculationBody](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/SysML-textual-bnf.kebnf#L1363-L1378), and the official Pilot explicitly overrides [ExpressionBody with CalculationBody](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.sysml.xtext/src/org/omg/sysml/xtext/SysML.xtext#L2436-L2439). This combined SysML grammar follows that first-party override; it does not present `calculationBodyPart` as a generic KerML-only replacement.

| Surface | Generic KerML KEBNF | SysML KEBNF/Pilot | Current PR #11 | Finding mapping |
|---|---|---|---|---|
| Braced body | `FunctionBodyPart` path | `CalculationBodyPart` override | `a.{ x }` and body members accepted without exact ambiguity | R3 body-scope alignment |
| Empty body | Context-dependent generic body | Explicit `SEMI` alternative | `a.;`, `a.?;`, `a->F;` accepted at expression entrypoint; root declarations add their outer terminator | R3 semicolon boundary |
| Body members plus result | Generic function members | Calculation items plus optional result | Private attributes, parameters, return members, and final results are accepted | R3 SysML behavior |

## R4: official comment and note boundary restored

The official lexical sources distinguish [KEBNF `MULTILINE_NOTE` and `REGULAR_COMMENT`](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L32-L46) and the Pilot exposes separate [hidden `ML_NOTE` and visible `REGULAR_COMMENT` terminals](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext#L569-L578). `REGULAR_COMMENT` is a model-owned comment body, not a `BaseExpression`; both the official [KEBNF](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1180-L1190) and [Pilot base-expression grammar](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext#L349-L378) exclude it.

Fix 54 restores the separate lexer terminals and hides `ML_NOTE`; Fix 55 removes the superseded `REGULAR_COMMENT` expression alternative. The EOF-qualified line-note rule reproduces the official Xtext/ANTLR3 tie: a same-line `//* ... */` can be consumed as `SL_NOTE`, while a newline-delimited `//* ... */` is recognized as hidden `ML_NOTE`.

| Example | Official Pilot direct run | Current PR #11 | Finding mapping |
|---|---|---|---|
| `a.{/* c */}` | Accept | Accept | R4 fixed: regular comment remains valid in body-comment position |
| `a.{x; /* c */}` | Accept | Accept | R4 fixed |
| `a.?{/* c */}` | Accept | Accept | R4 fixed |
| `a->f{/* c */}` | Accept | Accept | R4 fixed |
| `a.{//* c */}` | Reject; same-line `SL_NOTE` consumes the line | Reject | R4 fixed: note/comment lexical boundary |
| `a.{\n//* c */\n}` | Accept; hidden `ML_NOTE` leaves `}` visible | Accept | R4 fixed |
| `(/* c */)` | Reject; regular comments are not expressions | Reject | R4 fixed: no `baseExpression` comment placeholder |

## R6: contextual bare-name boundary aligned with direct Pilot behavior

The KEBNF has a broad lexical [NAME production](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L48-L60) and a separate [reserved-keyword declaration](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L112-L125); those declarative listings alone do not settle direct `OwnedExpression` acceptance. The official Pilot [Name rule](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/blob/fa709f28dfd49dfdb7ee83e4e19da2f57e0eb3aa/org.omg.kerml.expressions.xtext/src/org/omg/kerml/expressions/xtext/KerMLExpressions.xtext#L534-L550) is `ID | UNRESTRICTED_NAME`.

Fix 56 adds `TYPED` to the generated contextual-name alternative while retaining the lexer token needed by `typed by` syntax. It removes `LANGUAGE`, `LOCALE`, and `CROSSES` from that alternative. This follows direct official runtime behavior without pretending that the broad KEBNF keyword listing is itself an executable acceptance rule.

| Input | Official lexer/parser | Current PR #11 | Finding mapping |
|---|---|---|---|
| `typed` | Lexer emits `RULE_ID`; direct `OwnedExpression` accepts | Accepts through `TYPED` contextual-name alternative | R6 fixed: reverse mismatch |
| `language` | Literal keyword; direct `OwnedExpression` rejects | Rejects | R6 fixed: inherited over-acceptance removed |
| `locale` | Literal keyword; direct `OwnedExpression` rejects | Rejects | R6 fixed |
| `crosses` | Literal keyword; direct `OwnedExpression` rejects | Rejects | R6 fixed |

## Direct official-asset execution

The direct probes were run with the fixed official Pilot runtime JAR above. The harness used the official lexer, parser, token stream, grammar access, lookahead, diagnostics, and EOF checks. Only isolated semantic-object construction was replaced with no-op dynamic objects so syntax probing would not require a complete semantic model. This is independent of the repository's KEBNF-to-ANTLR conversion.

| Direct run | Result | Finding mapping |
|---|---|---|
| R1 probes: `a + if b ? c else d`; `-if b ? c else d`; `a ** if b ? c else d`; `a ?? if b ? c else d` | Official Pilot rejects all four | R1 residual normative gap |
| E4 classification/metaclassification probes: `a istype T + b`; `a istype T < b`; `a as T + b`; `a as T < b`; `a @@ T + b`; `a meta T + b` | Official Pilot rejects all probes | Current PR #11 rejects them; the KEBNF-recursive/Pilot-narrower boundary is disclosed below | E4 residual gap |
| Nested conditional condition probe: `if if a ? b else c ? d else e` | Official Pilot rejects (`syntaxErrors=true`, `parserErrors=1`, lookahead remains) | Current ANTLR accepts and reaches EOF; disclosed Pilot-narrower delta, not an equivalence claim |
| R2 valid probes: `a.{;}`; `a.{x;;}`; `a.{x; ;}`; `a.{x ; ;}`; `a.{y ; ;}` | Official Pilot accepts all five as nested result forms | R2a fixed |
| R2 malformed probes: `a.{;;}`; `a.{; x}`; `a.{x;; y}`; `a.{x;;; y}`; `a.{x; ; y}` | Official Pilot rejects all five | R2b fixed |
| R4 comment probes | Official Pilot accepts regular comments in body positions, rejects `(/* c */)`, rejects same-line `//*`, and accepts newline-delimited hidden `//*` | R4 fixed |
| R6 name probes | Official Pilot accepts `typed` and rejects `language`, `locale`, and `crosses` | R6 fixed |
| Full official fixture: `33. Analysis/Analysis Case Usage Example.sysml` | `accepted=true`, `parserErrors=0`, EOF `-1`; fixture SHA-256 `8061f236770a23a365026fa3565bdad1af381058deca50486d03d5efbe4fe93e` | Direct first-party root-parser evidence |

## Residual findings

### R1: KEBNF-recursive conditional operands remain an acceptance gap

The KEBNF derivation `BinaryOperatorExpression -> ArgumentMember -> ArgumentValue -> OwnedExpression` makes conditional operands recursively derivable because `OwnedExpression` includes `ConditionalExpression`. The exact source chain is [OwnedExpression](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L932-L940), [ConditionalExpression](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L942-L947), [ConditionalBinaryOperatorExpression and BinaryOperatorExpression](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L949-L969), [UnaryOperatorExpression](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L971-L977), and [ArgumentValue](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1003-L1010). The released Pilot rejects the unparenthesized right-hand, both-sided, and unary forms, while the current ANTLR grammar records the same concrete boundary. A broad acceptance experiment was not merged because trailing/nested forms introduced exact ANTLR ambiguities. The released Pilot also rejects `if if a ? b else c ? d else e`, while the current ANTLR grammar accepts it under the deterministic recursive rule. This PR therefore does not claim strict KEBNF/Pilot acceptance-set identity.

#### Exhaustive R1 matrix

The fixed matrix contains 136 cases: every one of the 23 binary operators is tested with a conditional right operand, left operand, and both operands; all four unary operators are tested with unparenthesized and parenthesized conditionals; nested condition/then/else forms, tail nesting, and parenthesized binary operands are included. The matrix invokes `ownedExpression` directly. Each KEBNF result was obtained by an independent fixed-point recognizer implementing only the pinned first-party productions; the recognizer did not consume generated ANTLR files. Each Pilot result was obtained by directly invoking the official Pilot lexer/parser/runtime described above.

| Matrix category | Examples | Count | Raw KEBNF derivability | Current ANTLR | Official Pilot | Evidence interpretation |
|---|---|---:|---:|---:|---:|---|
| Conditional core | `if b ? c else d`; `if if a ? b else c ? d else e`; `if a ? if b ? c else d else e`; `if a ? b else if c ? d else e` | 4 | 4/4 | 4/4 | 3/4 | The nested condition is the single ANTLR-only case; nested then/else forms are accepted by both. |
| Conditional right operand | `a + if b ? c else d`; `a ** if b ? c else d`; `a ?? if b ? c else d` (all 23 operators) | 23 | 23/23 | 0/23 | 0/23 | KEBNF-recursive, but rejected by both concrete parsers. |
| Conditional left operand | `if b ? c else d + a`; `if b ? c else d ** a`; `if b ? c else d ?? a` (all 23 operators) | 23 | 23/23 | 23/23 | 23/23 | Accepted by both concrete parsers. |
| Conditional on both sides | `if a ? b else c + if d ? e else f`; `if a ? b else c ** if d ? e else f`; `if a ? b else c ?? if d ? e else f` (all 23 operators) | 23 | 23/23 | 0/23 | 0/23 | KEBNF-recursive, but rejected by both concrete parsers. |
| Unary conditional, unparenthesized | `+if b ? c else d`; `-if b ? c else d`; `~if b ? c else d`; `not if b ? c else d`, plus four nested variants | 8 | 8/8 | 0/8 | 0/8 | KEBNF-recursive, but rejected by both concrete parsers. |
| Unary conditional, parenthesized | `+(if b ? c else d)`; `-(if b ? c else d)`; `~(if b ? c else d)`; `not (if b ? c else d)` | 4 | 4/4 | 4/4 | 4/4 | Parentheses enter the primary-expression path and remove the boundary gap. |
| Parenthesized binary operands | `a + (if b ? c else d)`; `(if b ? c else d) + a` (both orientations for all 23 operators) | 46 | 46/46 | 46/46 | 46/46 | Parenthesized forms are accepted by both concrete parsers. |
| Tail nesting | `a + if b ? c else d + e`; `a + if b ? c else d * e`; `a + b * if c ? d else e`; `a ?? if b ? c else d`; `a ** if b ? c else d` | 5 | 5/5 | 0/5 | 0/5 | KEBNF-recursive tail forms remain rejected by both concrete parsers. |

**Joint result:** all `136/136` cases are derivable from the raw KEBNF recognizer; current ANTLR and the official Pilot both accept `76`, both reject `59`, ANTLR accepts one that Pilot rejects, and Pilot accepts none that ANTLR rejects. Exact ambiguity count is `0` in the ANTLR run. The 59 shared rejections and the one ANTLR-only acceptance are reported as implementation/acceptance-set deltas, not silently promoted to normative KEBNF rules.

| Example | KEBNF reading | Official Pilot | Current PR #11 | Finding mapping |
|---|---|---|---|---|
| `a + if b ? c else d` | Recursively derivable | Reject | Reject | R1 open |
| `-if b ? c else d` | Recursively derivable | Reject | Reject | R1 open |
| `a ** if b ? c else d` | Recursively derivable | Reject | Reject | R1 open |
| `a ?? if b ? c else d` | Recursively derivable | Reject | Reject | R1 open |

### E4: classification and metaclassification continuations are KEBNF-recursive

The released KEBNF does not support the earlier statement that a classification suffix normatively terminates before additive or relational continuation. `OwnedExpression` includes `BinaryOperatorExpression`; binary operands reach `OwnedExpression` through `ArgumentMember` and `ArgumentValue`; and `ClassificationExpression` plus `MetaclassificationExpression` are themselves `OwnedExpression` alternatives. The examples below are therefore recursively derivable in the declarative KEBNF. Direct execution of the official Pilot rejects them, and the current PR #11 preserves that Pilot boundary. This is a disclosed KEBNF/Pilot acceptance gap, not a KEBNF rejection rule. Evidence: [OwnedExpression and binary operators](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L932-L962), [classification and metaclassification](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L979-L1001), and [argument operands](https://github.com/Systems-Modeling/SysML-v2-Release/blob/de1070ae8e79c21532b8004fc663d47b35d0e9fa/bnf/KerML-textual-bnf.kebnf#L1003-L1010).

| Example family | Examples | KEBNF reading | Official Pilot | Current PR #11 | Finding mapping |
|---|---|---|---|---|---|
| Classification | `a istype T + b`; `a istype T < b`; `a hastype T + b`; `a @ T + b` | Recursively derivable through `OwnedExpression` operands | Rejects | Rejects | E4 open |
| Cast | `a as T + b`; `a as T < b` | Recursively derivable through `OwnedExpression` operands | Rejects | Rejects | E4 open |
| Metaclassification and metadata | `a @@ T + b`; `a @@ T < b`; `a meta T + b`; `a meta T < b` | Recursively derivable through `OwnedExpression` operands | Rejects | Rejects | E4 open |

### Pilot-narrower probes retained as disclosed deltas

The KEBNF/Table 6 model permits the following recursive or left-associative forms. The released Pilot is narrower for the rows marked `Reject`, while it accepts the explicitly listed nested then/else forms. The current grammar follows the declarative/normative model for these cases; they are not silently presented as universally Pilot-equivalent.

| Example | KEBNF/Table 6 reading | Direct Pilot | Current PR #11 | Finding mapping |
|---|---|---|---|---|
| `a .. b .. c` | Left-associative range chain | Reject | Accept | Pilot implementation delta |
| `not -a`; `-not a`; `---a`; `~not a` | Recursive unary forms | Reject | Accept | Pilot implementation delta |
| `if if a ? b else c ? d else e` | Recursive conditional form | Reject (`syntaxErrors=true`, `parserErrors=1`) | Accept (EOF reached; no syntax error) | Pilot implementation delta; explicitly disclosed |
| `if a ? if b ? c else d else e`; `if a ? b else if c ? d else e` | Recursive conditional in the then/else operand | Accept | Accept | Pilot-supported recursive conditional form |

### R5: release revision persistence remains open

The upstream watcher updates the release tag/version and invokes generation with `--tag`, but [the watcher workflow](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/.github/workflows/watch-upstream.yml#L95-L102) does not persist the resolved immutable revision. [The generator's tag handling](https://github.com/HansBug/sysml-v2-grammar/blob/b3f52b388456d818a559bfd5b772374482006f3e/scripts/generate_grammar.py#L3411-L3417) changes in-memory configuration only. A future automated update can therefore commit grammar generated from one revision while `scripts/config.json` and conformance fixtures still point at another. The default pinned path is reproducible in this PR, but the watcher workflow needs a separate fix.

## Validation at `b3f52b38`

| Check | Result | Finding mapping |
|---|---:|---|
| `make generate` from pinned release revision | `53/56` patches applied; generated lexer/parser/ledger reproducible; token vocabulary is checked separately | Generator reproducibility |
| Fresh ANTLR token artifact comparison | Tracked `SysMLv2Lexer.tokens` is byte-identical to ANTLR 4.13.2 output from the committed lexer grammar | Generated artifact integrity |
| ANTLR expression regression harness | `147` cases passed with explicit EOF and exact-ambiguity checks | E1-E5, R1, R2, R4, R6 |
| Root parser regression cases | `9/9` valid and `3/3` invalid passed | Root embedding and EOF boundaries |
| Repository examples | `3/3` passed | Root parser smoke coverage |
| Official conformance fixtures | `309/309`: Standard Library `58/58`, Training `100/100`, Validation `56/56`, Examples `95/95` | Pinned official release corpus |
| Raw KEBNF R1 derivability matrix | `136/136` cases derivable from the cited first-party productions; no generated ANTLR grammar used by the recognizer | Normative/declarative R1 evidence |
| Official Pilot R1 direct matrix | `76` accepted, `60` rejected; no Pilot-only acceptance relative to current ANTLR; exact ANTLR ambiguity count `0` | Direct executable R1 evidence |
| Three-way R1 comparison | Both accept `76`, both reject `59`, ANTLR-only `1`, Pilot-only `0` | R1 acceptance-set disclosure |
| Independent adversarial ANTLR corpus | `299/299` passed; no exact ambiguity reports | Supplementary current-grammar stress evidence |
| Fresh ANTLR stress corpus | `12,167` operator triples + `1,863` atom/operator combinations + `20,000` random expressions; zero exact ambiguities | Supplementary current-grammar stress evidence |
| Seeded ANTLR/Pilot differential corpus | `20,000` unique cases: both accept `19,008`, both reject `519`, ANTLR-only `473`, Pilot-only `0`, exact ambiguity `0` | Direct official-runtime differential evidence; Pilot-narrower behavior |
| Independent ANTLR/Pilot differential corpus | `1,598` cases: both accept `1,248`, both reject `316`, ANTLR-only `34`, Pilot-only `0`, exact ambiguity `0` | Disclosed Pilot-narrower behavior |
| `make lint` | Ruff, format, yamllint, actionlint, pip-audit, and grammar drift all passed | Repository checks |
| `make contrib` | All grammars-v4 contribution checks passed | Generated SDK/contribution surface |
| `make sdk-archive SDK_JOBS=1` | All 10 ANTLR targets generated; archive passed `unzip -t` | Cross-target generation |
| `git diff --check` | Passed | Patch hygiene |

The independent adversarial and differential harnesses are supplementary evidence, not new CI artifacts committed by this PR. All claims above are scoped to the exact final commit and the pinned artifacts identified in the evidence table.

## Decision summary

| Surface | Decision in PR #11 |
|---|---|
| PR #10 precedence reversal | Confirmed correct for ANTLR emission, OMG Table 6 grouping, and direct Pilot behavior; preserved |
| R2 calculation-body separators | Fixed by generated Fix 53; valid nested results and malformed separator forms now match the direct Pilot boundary with zero exact ambiguity in the regression cases |
| R3 SysML body | Follows the first-party SysML/Pilot `CalculationBody` override, not a generic KerML-only claim |
| R4 comments/notes | Fixed by restoring separate `REGULAR_COMMENT`/`ML_NOTE` lexer behavior and removing comments from `baseExpression` |
| R6 contextual names | Fixed to match direct Pilot probes: `typed` accepted; `language`, `locale`, and `crosses` rejected |
| R1 conditional operands | Not silently broadened; four KEBNF-recursive/Pilot-rejected forms remain an explicit normative gap |
| E4 classification/metaclassification continuations | KEBNF recursively derives representative continuations; direct Pilot and PR #11 reject them | Disclosed KEBNF/Pilot acceptance gap; not presented as a normative KEBNF rejection |
| R5 release management | Not changed here; immutable revision persistence remains an open follow-up |

This body is evidence-first: each cumulative code change is mapped to a source-level OMG/KEBNF or official Pilot reference and to a concrete local or direct-runtime check. It explicitly discloses the R1, E4, and R5 boundaries and does not claim strict full KEBNF/Pilot acceptance-set equivalence.
