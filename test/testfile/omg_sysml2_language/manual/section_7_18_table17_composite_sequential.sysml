state compositeState1 {
    entry; then state1;
    state state1;
    transition first state1 accept trigger1 if guard1 do action1 then state2;
    state state2;
    then done;
}
