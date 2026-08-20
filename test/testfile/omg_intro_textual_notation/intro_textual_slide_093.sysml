attribute def WayPoint {
    time : TimeValue;
    position : LengthValue;
    speed : SpeedValue;
}
analysis def FuelEconomyAnalysis {
    subject vehicle : Vehicle;
    objective fuelEconomyAnalysisObjective { ... }
    // Additional parameters can be specified in the case body.
    in attribute scenario : WayPoint[*];
    // The steps of an analysis case are actions that, together, compute the analysis result.
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
        // The second step computes the fuel economy result, given the power profile determined in the first step.
        then action solveForFuelEconomy {
            in power : PowerValue[*] = solveForPower.power;
            out fuelEconomy : DistancePerVolumeValue;
            ...
        }
        return fuelEconomyResult : DistancePerVolumeValue;
        = solveForFuelEconomy.fuelEconomy;
        ... }
