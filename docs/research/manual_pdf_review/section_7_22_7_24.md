# Manual PDF Audit: SysML v2.0 Clauses 7.22--7.24

## Provenance and method

- **Source:** `/tmp/SysML-2.0-Language.pdf`
- **SHA-256:** `46e6c0476a6f1f34f367d57e039d56659bff75e41d2e4b3d37ca4cadea84a83a`
- **Document:** *Systems Modeling Language v2.0, Part 1*; 691 physical PDF pages.
- **Authority:** rendered PDF page images. Layout-text extraction was used only to cross-check transcription; it did not determine whether an item was source text, its boundaries, or its provenance.
- **Page mapping in this scope:** physical PDF page = printed page + 32. Printed pages 137--144 correspond to physical pages 169--176.

`independently_parseable` means the displayed snippet is a syntactically complete SysML unit after normalizing PDF-only line wrapping. It does **not** claim that referenced names resolve or that the snippet is semantically clean. `contextual_fragment` means that the displayed material is a compartment/body fragment, contains a literal placeholder, or otherwise needs an enclosing model context. All punctuation, comments, placeholders, and apparent source typos are retained. Indentation is normalized only where imposed by a narrow PDF table column.

## Coverage and counts

| Clause | Printed pages | Physical pages | Textual source snippets |
| --- | ---: | ---: | ---: |
| 7.22 Cases | 137--138 | 169--170 | 1 |
| 7.23 Analysis Cases | 138--141 | 170--173 | 7 |
| 7.24 Verification Cases | 141--144 | 173--176 | 10 |
| **Total** | **137--144** | **169--176** | **18** |

The 18 snippets comprise 14 `independently_parseable` snippets and 4 `contextual_fragment` snippets. Fourteen come from the textual-notation columns of Tables 21--22; four are prose-adjacent displayed examples. One source example crosses printed pages 140--141 / physical pages 172--173.

| Printed page | Physical page | New snippets | Continuations | IDs beginning on the page |
| ---: | ---: | ---: | ---: | --- |
| 137 | 169 | 0 | 0 | -- |
| 138 | 170 | 1 | 0 | C22-01 |
| 139 | 171 | 5 | 0 | A23-01--A23-05 |
| 140 | 172 | 2 | 0 | A23-06--A23-07 |
| 141 | 173 | 0 | A23-07 ends | -- |
| 142 | 174 | 4 | 0 | V24-01--V24-04 |
| 143 | 175 | 5 | 0 | V24-05--V24-09 |
| 144 | 176 | 1 | 0 | V24-10 |

## Source ledger

### C22-01

- **Source row:** 7.22.2, displayed case-definition example
- **Printed / physical pages:** 138 / 170
- **Classification:** `independently_parseable`
- **Context and dependencies:** `AutomationSystem` and `Person` must resolve for semantic validation. The `objective` body contains only documentation; no objective requirement is declared.
- **Exact normalized source:**

  ```sysml
  case def FaultRecovery {
      subject system : AutomationSystem;
      actor engineer : Person;
      objective {
          doc
          /* The engineer determines the cause of the system
           * fault and resolves it returning the system to
           * nominal operation.
           */
      }
  }
  ```

### A23-01

- **Source row:** Table 21, Analysis Case Definition, first textual-notation cell
- **Printed / physical pages:** 139 / 171
- **Classification:** `independently_parseable`
- **Context and dependencies:** `Subject1` and `assumption1` need definitions/resolution in a semantic fixture. The `doc /* '...' */` text is a literal source placeholder.
- **Exact normalized source:**

  ```sysml
  analysis def AnalysisDef1 {
      subject s1 : Subject1;
      objective {
          doc /* '...' */;
          assume assumption1;
      }
  }
  ```

### A23-02

- **Source row:** Table 21, Analysis Case Definition, compartment-stack textual-notation cell
- **Printed / physical pages:** 139 / 171
- **Classification:** `independently_parseable`
- **Context and dependencies:** No external model references; `/* members */` is an intentional comment placeholder.
- **Exact normalized source:**

  ```sysml
  analysis def AnalysisDef1 {
      /* members */
  }
  ```

### A23-03

- **Source row:** Table 21, Analysis Case, first textual-notation cell
- **Printed / physical pages:** 139 / 171
- **Classification:** `independently_parseable`
- **Context and dependencies:** `AnalysisDef1`, `mySubject`, and `assumption1` must resolve for semantic validation. The graphical and textual counterparts both show the `assume assumption1` form.
- **Exact normalized source:**

  ```sysml
  analysis analysis1 : AnalysisDef1 {
      subject redefines s1 = mySubject;
      objective {
          doc /* '...' */
          assume assumption1;
      }
  }
  ```

### A23-04

- **Source row:** Table 21, Analysis Case, compartment-stack textual-notation cell
- **Printed / physical pages:** 139 / 171
- **Classification:** `independently_parseable`
- **Context and dependencies:** `AnalysisDef1` must resolve for semantic validation; `/* members */` is intentional.
- **Exact normalized source:**

  ```sysml
  analysis analysis1 : AnalysisDef1 {
      /* members */
  }
  ```

### A23-05

- **Source row:** Table 21, Analyses Compartment textual-notation cell
- **Printed / physical pages:** 139 / 171
- **Classification:** `contextual_fragment`
- **Context and dependencies:** A compartment fragment with a literal `...` placeholder; it needs an owning element and definitions for `AnalysisDef1` and `AnalysisDef4`. Do not use unchanged as a parser fixture.
- **Exact normalized source:**

  ```sysml
  analysis analysis1 : AnalysisDef1 {
      ...
      analysis analysis4 : AnalysisDef4;
  }
  ```

### A23-06

- **Source row:** 7.23.2, displayed FuelEconomyAnalysis definition
- **Printed / physical pages:** 140 / 172
- **Classification:** `independently_parseable`
- **Context and dependencies:** `Vehicle`, `DistancePerVolumeValue`, and `FuelEconomyRequirement` must resolve. The trailing `// ...` is a literal source comment, not an omitted continuation.
- **Exact normalized source:**

  ```sysml
  analysis def FuelEconomyAnalysis {
      subject vehicle : Vehicle;
      return fuelEconomyResult : DistancePerVolumeValue;

      objective fuelEconomyAnalysisObjective {
          doc
          /*
           * The objective of this analysis is to determine whether the
           * subject vehicle can satisfy the fuel economy requirement.
           */

          requirement : FuelEconomyRequirement;
      }
      // ...
  }
  ```

### A23-07

- **Source row:** 7.23.3, displayed engineTradeStudy trade-off-analysis example
- **Printed / physical pages:** 140--141 / 172--173
- **Classification:** `independently_parseable`
- **Context and dependencies:** Requires `TradeStudy`, `Engine`, `MaximizeObjective`, `PowerRollup`, `MassRollup`, `EfficiencyRollup`, `CostRollup`, `Real`, `EngineEvaluation`, `engine4cyl`, `engine6cyl`, and the inherited `alternative` feature. The page break occurs immediately after `in engine = anEngine;` in `powerRollup`; no code is omitted.
- **Exact normalized source:**

  ```sysml
  analysis engineTradeStudy : TradeStudy {
      // The subject is bound to the two alternatives to be studied.
      subject : Engine = (engine4cyl, engine6cyl);

      // The objective is to find the alternative that has the
      // maximum value for the evaluationFunction.
      objective : MaximizeObjective;

      // For each one of the alternatives, the evaluationFunction
      // produces a numerical evaluation result.
      calc :>> evaluationFunction {
          in part anEngine : Engine :>> alternative;

          calc powerRollup: PowerRollup {
              in engine = anEngine;
              return power;
          }
          calc massRollup: MassRollup {
              in engine = anEngine;
              return mass;
          }
          calc efficiencyRollup: EfficiencyRollup {
              in engine = anEngine;
              return efficiency;
          }
          calc costRollup: CostRollup {
              in engine = anEngine;
              return cost;
          }

          return :>> result : Real = EngineEvaluation(
              power = powerRollup.power,
              mass = massRollup.mass,
              efficiency = efficiencyRollup.efficiency,
              cost = costRollup.cost
          );
      }

      // The selected alternative will be the one that has the
      // maximum value for the evaluationFunction.
      return part :>> selectedAlternative : Engine;
  }
  ```

### V24-01

- **Source row:** Table 22, Verification Case Definition, first textual-notation cell
- **Printed / physical pages:** 142 / 174
- **Classification:** `independently_parseable`
- **Context and dependencies:** `Subject1` and `requirement1` must resolve. The document placeholder `doc /* '...' */` is literal source.
- **Exact normalized source:**

  ```sysml
  verification def VerificationDef1 {
      subject s1 : Subject1;
      objective {
          doc /* '...' */
          verify requirement1;
      }
  }
  ```

### V24-02

- **Source row:** Table 22, Verification Case Definition, compartment-stack textual-notation cell
- **Printed / physical pages:** 142 / 174
- **Classification:** `independently_parseable`
- **Context and dependencies:** No external model references; `/* members */` is intentional.
- **Exact normalized source:**

  ```sysml
  verification def VerificationDef1 {
      /* members */
  }
  ```

### V24-03

- **Source row:** Table 22, Verification Case, first textual-notation cell
- **Printed / physical pages:** 142 / 174
- **Classification:** `independently_parseable`
- **Context and dependencies:** `VerificationDef1`, `mySubject`, and `requirement1` must resolve. The graphical counterpart says `verify requirement2`, but the visually confirmed textual source says `verify requirement1;`.
- **Exact normalized source:**

  ```sysml
  verification verification1 : VerificationDef1 {
      subject redefines s1 = mySubject;
      objective {
          doc /* '...' */
          verify requirement1;
      }
  }
  ```

### V24-04

- **Source row:** Table 22, Verification Case, compartment-stack textual-notation cell
- **Printed / physical pages:** 142 / 174
- **Classification:** `independently_parseable`
- **Context and dependencies:** `VerificationDef1` must resolve; `/* members */` is intentional.
- **Exact normalized source:**

  ```sysml
  verification verification1 : VerificationDef1 {
      /* members */
  }
  ```

### V24-05

- **Source row:** Table 22, Verifications Compartment textual-notation cell
- **Printed / physical pages:** 143 / 175
- **Classification:** `contextual_fragment`
- **Context and dependencies:** The outer braces are a compartment body, not an independently owned model unit. It also refers to `VerificationDef1`, `verification10`, and `verification11`; `/* ... */` is intentional.
- **Exact normalized source:**

  ```sysml
  {
      verification verification1 : VerificationDef1 [1..*]
          ordered nonunique;
      /* ... */
      perform verification verification10;
      verification verification11 {
          verification 'verification11.1';
          verification 'verification11.2';
      }
  }
  ```

### V24-06

- **Source row:** Table 22, Verification Methods Compartment textual-notation cell
- **Printed / physical pages:** 143 / 175
- **Classification:** `contextual_fragment`
- **Context and dependencies:** Intended as a compartment item and depends on the `VerificationMethodKind` library enumeration. The visually printed absence of a comma after `VerificationMethodKind::demo` is retained exactly.
- **Exact normalized source:**

  ```sysml
  metadata VerificationMethod {
      kind = (
          VerificationMethodKind::inspect,
          VerificationMethodKind::demo
          VerificationMethodKind::analyze,
          VerificationMethodKind::test);
  }
  ```

### V24-07

- **Source row:** Table 22, Verifies Compartment textual-notation cell
- **Printed / physical pages:** 143 / 175
- **Classification:** `contextual_fragment`
- **Context and dependencies:** An `objective` body that must be owned by a case/verification context; `requirement1` and `requirement2` must resolve.
- **Exact normalized source:**

  ```sysml
  objective {
      verify requirement1;
      verify requirement2;
  }
  ```

### V24-08

- **Source row:** Table 22, Verify textual-notation cell, requirement declaration
- **Printed / physical pages:** 143 / 175
- **Classification:** `independently_parseable`
- **Context and dependencies:** `Requirement1` must resolve for semantic validation.
- **Exact normalized source:**

  ```sysml
  requirement requirement1: Requirement1;
  ```

### V24-09

- **Source row:** Table 22, Verify textual-notation cell, verification declaration
- **Printed / physical pages:** 143 / 175
- **Classification:** `independently_parseable`
- **Context and dependencies:** `VerificationCase1` and `requirement1` must resolve. It shares a single Table 22 textual-notation cell with V24-08, but is retained as a separate reusable declaration.
- **Exact normalized source:**

  ```sysml
  verification verificationCase1 : VerificationCase1 {
      objective {
          verify requirement1;
      }
  }
  ```

### V24-10

- **Source row:** 7.24.2, displayed VehicleMassTest verification-case definition
- **Printed / physical pages:** 144 / 176
- **Classification:** `independently_parseable`
- **Context and dependencies:** The imported `VerificationCases` library must be available. `Vehicle`, `ISQ::mass`, `VerdictKind`, `PassIf`, and `vehicleMassRequirement` must resolve. The source visibly spells `VerificationMthodKind` (missing `e`) and `statisfies`; these spellings are preserved rather than corrected.
- **Exact normalized source:**

  ```sysml
  verification def VehicleMassTest {
      import VerificationCases::*;

      subject testVehicle : Vehicle;
      objective vehicleMassVerificationObjective {
          // The subject of the verify is automatically bound to "testVehicle".
          verify vehicleMassRequirement;
      }

      metadata VerificationMethod {
          kind = VerificationMthodKind::test;
      }

      action collectData {
          in part testVehicle : Vehicle = VehicleMassTest::testVehicle;
          out massMeasured :> ISQ::mass;
      }
      action processData {
          in massMeasured :> ISQ::mass = collectData.massMeasured;
          out massProcessed :> ISQ::mass;
      }
      action evaluateData {
          in massProcessed :> ISQ::mass = processData.massProcessed;
          out verdict : VerdictKind =
              // Check that "testVehicle" statisfies "vehicleMassRequirement"
              // if its mass equals 'massProcessed'.
              PassIf(vehicleMassRequirement(
                  vehicle = testVehicle,
                  massActual = massProcessed)
              );
      }

      return verdict : VerdictKind = evaluateData.verdict;
  }
  ```

## Explicit exclusions

- **Outside-clause continuation at printed page 137 / physical page 169:** the page-top `satisfy rqts : VehicleRequirementsGroup;` and closing brace belong to the preceding Clause 7.21 example, not Clause 7.22.
- **Clause 7.22.1, 7.23.1, and 7.24.1 prose:** definitions, lists of verdict values, and the numbered verification workflow are explanatory prose, not rendered SysML source blocks.
- **All graphical-notation material:** code-like labels in the graphical columns of Tables 21 and 22, including `analysis1 : AnalysisDef1`, `verify requirement1`, and compartment labels, are diagram labels rather than textual-notation source. They are not source rows in this ledger.
- **Table 22, Verified Requirements Compartment:** this row has no textual-notation source content on printed page 143 / physical page 175.
- **References and library names in running prose:** clause numbers, metamodel references, and isolated names such as `PassIf`, `TradeStudy`, and `VerificationMethod` in prose are not separate source rows; occurrences inside displayed code are retained above.
- **The start of Clause 7.25:** printed page 145 / physical page 177 was checked only to establish the scope boundary and is excluded.
- **No inferred repair:** literal `...` / `/* ... */` placeholders and visually printed punctuation or apparent typos were retained; no omitted enclosing context, definitions, commas, or spelling corrections were inferred.

## Audit conclusion

Rendered images for every in-scope physical page 169--176 were inspected. The ledger records all 18 visually confirmed textual source snippets for Clauses 7.22--7.24, including the single cross-page TradeStudy example and every textual-notation cell in Tables 21 and 22. No repository file was edited.
