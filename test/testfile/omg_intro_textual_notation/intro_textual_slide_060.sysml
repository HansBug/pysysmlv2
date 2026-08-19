// An occurrence definition defines a class of occurrences, without committing to whether they are structural or behavioral.
occurrence def CruiseControlInteraction {
    ref part :>> driver;
    ref part :>> vehicle;
    // A message asserts that there is a transfer of some payload of a certain type from one occurrence to another (specifying the payload type is optional).
    message setSpeedMessage of SetSpeed
        from driver.setSpeedSent
        to vehicle.cruiseController.setSpeedReceived;
    message sensedSpeedMessage of SensedSpeed
        from vehicle.speedometer.sensedSpeedSent
        to vehicle.cruiseController.sensedSpeedReceived;
    message fuelCommandMessage of FuelCommand
        from vehicle.cruiseController.fuelCommandSent
        to vehicle.engine.fuelCommandReceived;
    // Messages can be explicitly ordered. Otherwise, they are only partially ordered by the time-ordering of their respective source and target events.
    first setSpeedMessage then sensedSpeedMessage;
}
