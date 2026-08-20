state def OperationalStates {
    entry action initial { out attribute isStarting : Boolean; }
    if not initial.isStarting then off;
    if initial.isStarting then starting;
    state off;
    state starting;
    state on;
}
