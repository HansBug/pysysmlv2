analysis def FuelEconomyAnalysis {
    subject vehicle : Vehicle;
    return fuelEconomyResult : DistancePerVolumeValue;

    objective fuelEconomyAnalysisObjective {
        doc
        /*
         * The objective of this analysis is to determine whether the
         * subject vehicle can satisfy the fuel economy requirement.
         */

        requirement : FuelEconomyRequirement;
    }
    // ...
}
