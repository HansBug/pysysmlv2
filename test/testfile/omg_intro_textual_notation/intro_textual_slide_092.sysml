// An analysis case definition defines the computation of the result of analyzing some subject, meeting an objective.
analysis def FuelEconomyAnalysis {
    // The subject may be specified similarly to the subject of a requirement definition.
    subject vehicle : Vehicle;
    // The objective is a requirement on the result of the analysis case.
    objective fuelEconomyAnalysisObjective {
        doc /*
        * The objective of this analysis is to determine whether the
        * subject vehicle can satisfy the fuel economy requirement.
        */
        // The analysis objective is specified as a requirement, allowing both assumed and required constraints.
        assume constraint {
            vehicle.wheelDiameter == 33['in'] and
            vehicle.driveTrainEfficiency == 0.4
        }
        require constraint {
            fuelEconomyResult > 30[mi / gallon]
        }
    }
    ...
    // The analysis result is declared as a return result (as for a calculation definition).
    return fuelEconomyResult : DistancePerVolumeValue = ...;
}
