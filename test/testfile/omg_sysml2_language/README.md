# OMG SysML 2.0 Language examples

These files are repository-owned copies of the reviewed textual examples in
the OMG *SysML 2.0 Language* specification, especially clauses 7.18.1--7.18.4
(printed pages 114--122).  They are deliberately stored below `test/testfile`
so tests do not read the temporary PDF, a network URL, or the upstream release
checkout at runtime.

The source ledger is
`docs/research/omg_sysml2_language_examples.json`.  Each entry records its
clause, printed page, normalized source text, parser status, and the name of
the corresponding fixture.  The PDF itself is identified there by its OMG URL
and SHA-256 digest.

`section7/` contains one file per reviewed example.  The AST golden file is
generated only after parser behavior is verified and excludes `span`; tests
assert every remaining dataclass field and then run a separate canonical
round-trip check.  A second parse is therefore an additional invariant, never
the expected-AST oracle.

The snippets remain short excerpts from the OMG specification.  Keep the
copyright and license notices of the specification with any redistribution.
