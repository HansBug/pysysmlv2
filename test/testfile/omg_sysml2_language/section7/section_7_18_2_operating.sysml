state def Operating {
    entry assign stateCode := StateCodes::Operating;
    do send new ReadySignal() to Controller;
}
