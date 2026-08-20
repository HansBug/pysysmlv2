// Ports are also suboccurrences of the parts that contain them.
part driver_b : Driver {
    port setSpeedPort {
        out setSpeed : SetSpeed;
    }
}
// In this model, event occurrences are realized by values leaving from and arriving at ports.
interface driver_b.setSpeedPort to vehicle_b.setSpeedPort {
    flow of SetSpeed from driver_b.setSpeedPort.setSpeed
        to vehicle_b.setSpeedPort.setSpeed;
}
part vehicle_b : Vehicle {
    port setSpeedPort {
        in setSpeed : SetSpeed;
    }
    part cruiseController_b : CruiseController {
        port setSpeedPort {
            in setSpeed : SetSpeed = vehicle_b.setSpeedPort.setSpeed;
        }
        port sensedSpeedPort {
            in sensedSpeed : SetSpeed;
        }
        ...
    }
    // Messages are realized by explicit flows between features of ports.
    flow of SensedSpeed from speedometer_b.sensedSpeedPort.sensedSpeed
        to cruiseController_b.sensedSpeedPort.sensedSpeed;
    part speedometer_b : Speedometer {
        port sensedSpeedPort {
            out sensedSpeed : SensedSpeed;
        }
    }
    ...
