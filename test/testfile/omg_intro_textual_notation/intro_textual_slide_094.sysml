part vehicleFuelEconomyAnalysisContext {
    requirement vehicleFuelEconomyRequirements{subject vehicle : Vehicle; ... }
    attribute cityScenario : WayPoint[*] = { ... };
    attribute highwayScenario : WayPoint[*] = { ... };
    // The previously defined analysis is carried out for a specific vehicle configuration for two different scenarios.
    analysis cityAnalysis : FuelEconomyAnalysis {
        subject vehicle = vehicle_c1;
        in scenario = cityScenario;
    }
    analysis highwayAnalysis : FuelEconomyAnalysis {
        subject vehicle = vehicle_c1;
        in scenario = highwayScenario;
    }
    part vehicle_c1 : Vehicle {
        ...
        attribute :>> fuelEconomy_city = cityAnalysis.fuelEconomyResult;
        attribute :>> fuelEconomy_highway = highwayAnalysis.fuelEconomyResult;
    }
    satisfy vehicleFuelEconomyRequirements by vehicle_c1;
}
