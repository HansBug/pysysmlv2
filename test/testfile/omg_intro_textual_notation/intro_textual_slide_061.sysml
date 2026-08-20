occurrence def CruiseControlInteraction {
    ref part driver : Driver {
        // An event can also be specified by reference to an identified occurrence (such as the source or target of a message).
        event setSpeedMessage.sourceEvent;
    }
    ref part vehicle : Vehicle {
        part cruiseController : CruiseController {
            event setSpeedMessage.targetEvent;
            then event sensedSpeedMessage.targetEvent;
            then event fuelCommandMessage.sourceEvent;
        }
        part speedometer : Speedometer {
            event sensedSpeedMessage.sourceEvent;
        }
        part engine : Engine {
            event fuelCommandMessage.targetEvent;
        }
    }
    // Each message has a sourceEvent and targetEvent, even if it is not explicitly identified in the message declaration.
    message setSpeedMessage of SetSpeed;
    then message sensedSpeedMessage of SensedSpeed;
    message fuelCommandMessage of FuelCommand;
}
