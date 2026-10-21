state operatingStates {
    entry action initial;
    state off;
    state starting;
    state on {
        entry performSelfTest;
        do providePower;
        exit applyParkingBrake;
        constraint { electricalPower <= 500[W] }
    }
    transition initial then off;
    transition 'off-starting'
        first off
        accept ignitionCmd : IgnitionCmd via ignitionCmdPort
            if ignitionCmd.ignitionOnOff == IgnitionOnOff::on and brakePedalDepressed
        do send new StartSignal() to controller
        then starting;
    transition 'starting-on'
        first starting
        accept VehicleOnSignal
        then on;
    transition 'on-off'
        first on
        accept VehicleOffSignal
        do send new OffSignal() to controller
        then off;
}
