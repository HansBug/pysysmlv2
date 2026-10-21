action def ProvidePower {
    in item fuelCmd : FuelCmd;
    out wheelToRoadTorque : TorqueValue[2];
}
item def FuelCmd {
    attribute throttleLevel : Real;
}
port def FuelPort {
    out item fuel : Fuel;
}
item def Fuel {
    attribute fuelMass :> ISQ::mass;
}
interface def FuelInterface {
    end fuelOutPort : FuelPort;
    end fuelInPort : ~FuelPort;
    flow of Fuel from fuelOutPort.fuel to fuelInPort.fuel;
}
enum def FuelKind { gas; diesel; }
