// The default name for a message payload is payload.
// Note that a payload declaration without a colon names the type of the payload, not the payload itself.
message setSpeedMessage of SetSpeed
    from driver.setSpeedSent
    to vehicle.cruiseController.setSpeedReceived;
then message sensedSpeedMessage of SensedSpeed
    from vehicle.speedometer.sensedSpeedSent
    to vehicle.cruiseController.sensedSpeedReceived;
then message fuelCommandMessage of fuelCommand : FuelCommand
    from vehicle.cruiseController.fuelCommandSent
    to vehicle.engineController.fuelCommandReceived;
// The payload of a message can also be bound to a specific value. In this case, the fuelCommandMessage payload is forwarded by the engineController to the engine.
then message fuelCommandForwardingMessage
// The payload of a message can be declared with a name for reference.
of fuelCommand : FuelCommand = fuelCommandMessage.fuelCommand
    from vehicle.engineController.fuelCommandForwarded
    to vehicle.engine.fuelCommandReceived;
