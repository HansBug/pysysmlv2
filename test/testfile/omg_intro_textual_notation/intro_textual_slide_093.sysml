attribute def WayPoint {
    time : TimeValue;
    position : LengthValue;
    speed : SpeedValue;
}
analysis def FuelEconomyAnalysis {
    subject vehicle : Vehicle;
    objective fuelEconomyAnalysisObjective { ... }
    in attribute scenario : WayPoint[*];
    // The first step solves for the engine power needed for a given position/velocity scenario.
    action solveForPower {
        out power: PowerValue[*];
        out acceleration: AccelerationValue[*];
        assert constraint {
            (1..size(scenario)-1)->forAll {in i : Positive;
                StraightLineDynamicsEquations (
                power#(i), vehicle.mass,
                scenario.time#(i+1) - scenario.time#(i),
                scenario.position#(i), scenario.speed#(i),
                scenario.position#(i+1), scenario.speed#(i+1),
                acceleration#(i+1)))
            }
        }
        then action solveForFuelEconomy {
            in power : PowerValue[*] = solveForPower.power;
            out fuelEconomy : DistancePerVolumeValue;
            ...
        }
        return fuelEconomyResult : DistancePerVolumeValue;
        = solveForFuelEconomy.fuelEconomy;
        ... }
