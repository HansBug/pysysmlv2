state def OnOff3 {
    in attribute isInitOff : Boolean;
    in attribute isEnabled : Boolean;
    port commPort;
    entry action init;
    transition first init if isInitOff then off;
    transition first init if not isInitOff then on;
    state off;
    state on;
    transition off_on first off accept TurnOn via commPort if isEnabled then on;
    transition on_off first on accept after 5[min] if isEnabled then off;
}
