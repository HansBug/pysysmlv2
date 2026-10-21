part vehicle_b : Vehicle {
    port fuelCmdPort redefines pwrCmdPort;
    port vehicleToRoadPort redefines vehicleToRoadPort {
        port wheelToRoadPort1;
        port wheelToRoadPort2;
    }
    part fuelTank : FuelTank {
        port fuelOutPort;
    }
    part rearAxleAssembly {
        port shaftPort_d;
        part rearWheel1 : Wheel {
            port :>>wheelToRoadPort;
            port :>>wheelToAxlePort;
        }
        part rearWheel2 : Wheel {
            port :>>wheelToRoadPort;
            port :>>wheelToAxlePort;
        }
        part differential : Differential {
            port shaftPort_d;
            port leftDiffPort;
            port rightDiffPort;
        }
        part rearAxle {
            part leftHalfAxle : HalfAxle {
                port leftAxleToDiffPort;
                port leftAxleToWheelPort;
            }
            part rightHalfAxle : HalfAxle {
                port rightAxleToDiffPort;
                port rightAxleToWheelPort;
            }
        }
    }
    part starterMotor : StarterMotor {
        port ignitionCmdPort;
        port gearPort;
    }
    part engine : Engine {
        port fuelCmdPort;
        port drivePwrPort : DrivePwrPort;
        port fuelInPort;
        port flyWheelPort;
        port controlPort;
    }
    part transmission : Transmission {
        port clutchPort : ~DrivePwrPort;
        port shaftPort_a;
    }
    part driveshaft : Driveshaft {
        port shaftPort_b;
        port shaftPort_c;
    }
    part vehicleSoftware : VehicleSoftware {
        part vehicleController {
            port controlPort;
        }
    }
    //connections
    bind engine.fuelCmdPort = fuelCmdPort;
    bind starterMotor.ignitionCmdPort = ignitionCmdPort;
    interface engineToTransmissionInterface : EngineToTransmissionInterface
        connect engine.drivePwrPort to transmission.clutchPort;
    interface fuelInterface : FuelInterface
        connect fuelTank.fuelOutPort to engine.fuelInPort;
    connect vehicleSoftware.vehicleController.controlPort
        to engine.controlPort;
    connect starterMotor.gearPort
        to engine.flyWheelPort;
    connect transmission.shaftPort_a
        to driveshaft.shaftPort_b;
    connect driveshaft.shaftPort_c
        to rearAxleAssembly.shaftPort_d;
    bind rearAxleAssembly.rearWheel1.wheelToRoadPort
        = vehicleToRoadPort.wheelToRoadPort1;
    bind rearAxleAssembly.rearWheel2.wheelToRoadPort
        = vehicleToRoadPort.wheelToRoadPort2;
}
