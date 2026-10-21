analysis fuelEconomyAnalysis {
    in attribute scenario : Scenario;
    subject = vehicle_b;
    objective fuelEconomyAnalysisObjective {
        doc /* estimate the vehicle fuel economy */
    }
    attribute distance = TraveledDistance(scenario);
    attribute tpd_avg = AverageTravelTimePerDistance(scenario);
    attribute bsfc = ComputeBSFC(vehicle_b.engine);
    attribute f_a =
        BestFuelConsumptionPerDistance(vehicle_b.mass, bsfc, tpd_avg, distance);
    attribute f_b = IdlingFuelConsumptionPerTime(vehicle_b.engine);
    return attribute calculatedFuelEconomy :> distancePerVolume =
        FuelConsumption(f_a, f_b, tpd_avg);
}
