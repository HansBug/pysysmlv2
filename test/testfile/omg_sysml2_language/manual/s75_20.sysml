package P7 {
    public import P1::A {
        /* The imported membership is visible outside P7. */
    }

    private import P4::* {
        doc /* None of the imported memberships are visible
             * outside of P7. */
    }
}
