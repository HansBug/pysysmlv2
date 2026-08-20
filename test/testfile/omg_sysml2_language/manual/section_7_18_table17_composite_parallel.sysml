state compositeState2 parallel {
    state state1 {
        entry; then 'state1.1';
        state 'state1.1';
    }
    state state2 {
        entry; then 'state2.1';
        state 'state2.1';
    }
}
