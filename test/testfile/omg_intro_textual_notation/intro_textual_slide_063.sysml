// An interaction can be realized by many different models. A valid realization must have suboccurrences that can be identified with all the events and messages in the interaction.
part driver_a : Driver {
    perform action driverBehavior {
        send new SetSpeed() to vehicle_a;
    }
}
part vehicle_a : Vehicle {
    part cruiseController_a : CruiseController {
        perform action controllerBehavior {
            // In this model, event occurrences are realized by nested send and accept actions.
            accept SetSpeed via vehicle_a;
            then accept SensedSpeed via cruiseController_a;
            then send new FuelCommand() to engine_a;
        }
    }
    part speedometer_a : Speedometer {
        perform action speedometerBehavior {
            // Messages are realized by the implicit transfers between send actions and corresponding accept actions.
            send new SensedSpeed() to cruiseController_a;
        }
    }
    // In more realistic cases, a realizing model will have more extensive behavior, only a subset of which will conform to any one interaction model.
    part engine_a : Engine {
        perform action engineBehavior {
            accept FuelCommand via engine_a;
        }
    }
}
