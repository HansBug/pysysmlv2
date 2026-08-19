action def ChargeBattery {
    // A loop action repeatedly performs a body action.
    // Control-structure actions provide a structured alternative to control nodes for conditionals and looping.
    // This is the body action, which is given the name charging. (The default name is body.)
    // A loop action can also begin with while (instead of loop), introducing a Boolean condition that terminates the loop when it is false.
    loop action charging {
        action monitor : MonitorBattery {
            out charge;
        }
        // An if action performs its body if a Boolean condition is true. (It can also have an else part, which is performed if the condition is false.)
        // If used in this way represents an action, not a succession.
        then if monitor.charge < 100 {
            action addCharge : AddCharge {
                in charge = monitor.charge;
            }
        }
    // until introduces a Boolean condition that terminates the loop when it is true.
    } until charging.monitor.charge >= 100;
    then action endCharging : EndCharging;
    then done;
}
