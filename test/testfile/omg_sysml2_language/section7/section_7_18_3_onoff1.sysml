state def OnOff1 {
    entry;
    then off;
    state off;
    state on;
    transition off_on first off then on;
    transition on_off first on then off;
}
