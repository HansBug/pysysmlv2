package P2 {
    private import P1::A;
    private import P1::C; // Imported with name "C".
    package Q {
        import C; // "C" is re-imported from P2 into Q.
    }
}
