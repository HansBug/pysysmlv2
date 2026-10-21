state healthStates {
    entry action initial;
    do senseTemperature {
        out temp;
    }
    state normal;
    state maintenance;
    state degraded;
    transition initial then normal;
    transition 'normal-maintenance'
        first normal
        accept at maintenanceTime
        then maintenance;
    transition 'normal-degraded'
        first normal
        accept when senseTemperature.temp > Tmax
        do send new OverTemp() to controller
        then degraded;
    transition 'maintenance-normal'
        first maintenance
        accept ReturnToNormal
        then normal;
    transition 'degraded-normal'
        first degraded
        accept ReturnToNormal
        then normal;
}
