part driver : Driver {
    // An event occurrence is a reference to something that happens during the lifetime of another occurrence.
    event occurrence setSpeedSent;
}
part vehicle : Vehicle {
    part cruiseController : CruiseController {
        event occurrence setSpeedReceived;
        // Event occurrences can be sequenced as usual using succession.
        then event occurrence sensedSpeedReceived;
        then event occurrence fuelCommandSent;
    }
    part speedometer : Speedometer {
        event occurrence sensedSpeedSent;
    }
    part engine : Engine {
        event occurrence fuelCommandReceived;
    }
}
