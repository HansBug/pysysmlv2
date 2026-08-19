item def Abort;
state def OnOff6 {
    port commPort;
    entry; then off;
    state off;
    accept TurnOn via commPort then on;
    accept Abort via commPort then stop;
    state on;
    accept after 5[min] then done;
    action stop terminate;
}
