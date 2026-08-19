item def TurnOn;
state def OnOff2 {
    port commPort;
    entry;
    then off;
    state off;
    state on;
    transition off_on first off accept TurnOn via commPort then on;
    transition on_off first on accept after 5[min] then off;
}
