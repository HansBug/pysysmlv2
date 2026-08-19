action def PowerUp;
item def TimeoutSignal;
state def OnOff5 {
    in attribute isInitOff;
    in attribute isEnabled;
    port commPort;
    entry;
    if isInitOff then off;
    if not isInitOff then on;
    state off;
    accept TurnOn via commPort if isEnabled do action powerUp : PowerUp; then on;
    state on;
    accept after 5[min] if isEnabled do send new TimeoutSignal() via commPort; then off;
}
