action def PowerUp;
item def TimeoutSignal;
state def OnOff4 {
    in attribute isInitOff;
    in attribute isEnabled;
    port commPort;
    entry action init;
    transition first init if isInitOff then off;
    transition first init if not isInitOff then on;
    state off;
    state on;
    transition off_on first off if isEnabled accept TurnOn via commPort do action powerUp : PowerUp; then on;
    transition on_off first on if isEnabled accept after 5[min] do send new TimeoutSignal() via commPort then off;
}
