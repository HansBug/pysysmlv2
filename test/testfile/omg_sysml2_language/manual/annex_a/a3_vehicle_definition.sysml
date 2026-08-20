part def Vehicle {
    attribute mass :> ISQ::mass;
    attribute dryMass :> ISQ::mass;
    attribute cargoMass :> ISQ::mass;
    attribute position :> ISQ::length;
    attribute velocity :> ISQ::speed;
    attribute acceleration :> ISQ::acceleration;
    attribute electricalPower :> ISQ::power;
    attribute Tmax :> ISQ::temperature;
    attribute maintenanceTime : Time::DateTime;
    attribute brakePedalDepressed : Boolean;
    port ignitionCmdPort : IgnitionCmdPort;
    port pwrCmdPort : PwrCmdPort;
    port vehicleToRoadPort : VehicleToRoadPort;
    perform action providePower;
    perform action provideBraking;
    perform action controlDirection;
    perform action performSelfTest;
    perform action applyParkingBrake;
    perform action senseTemperature;
    exhibit state vehicleStates;
}
