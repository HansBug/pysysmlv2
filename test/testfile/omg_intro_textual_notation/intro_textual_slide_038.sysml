action def ChargeBattery {
    first start;
    then merge continueCharging;
    then action monitor : MonitorBattery {
        out batteryCharge : Real;
    }
    // A decision node (decide keyword) chooses exactly one successor to happen after it.
    then decide;
    // A decision node is typically followed by one or more conditional successions (the last “if … then” can be replaced by “else”).
    if monitor.batteryCharge < 100 then addCharge;
    if monitor.batteryCharge >= 100 then endCharging;
    action addCharge : AddCharge {
        in charge = monitor.batteryCharge;
    }
    then continueCharging;
    action endCharging : EndCharging;

    // References the end of the action as the target of a succession.
    then done;
}
