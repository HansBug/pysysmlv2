// The TradeStudy analysis definition from the TradeStudies domain library model provides a general framework for defining basic trade study analyses.
// A trade-off study is an analysis with the objective of selecting the optimum alternative from a given set based on an evaluation of each alternative.
analysis engineTradeStudy : TradeStudies::TradeStudy {
    // Bind the analysis subject to the set of study alternatives. Select either MaximizeObjective or MinimizeObjective.
    subject : Engine = (engine4cyl, engine6cyl);
    objective : MaximizeObjective;
    // Redefine the evaluationFunction calculation to provide an evaluation of each one of the alternatives.
    calc :>> evaluationFunction {
        in part anEngine :>> alternative : Engine;
        calc powerRollup: PowerRollup {in engine = anEngine;
            return power : ISQ::PowerValue; }
        calc massRollup: MassRollup {in engine = anEngine;
            return mass : ISQ::MassValue; }
        calc efficiencyRollup: EfficiencyRollup {in engine = anEngine;
            return efficiency : Real; }
        calc costRollup: CostRollup {in engine = anEngine;
            return cost : Real; }
        return :>> result : Real = EngineEvaluation(
        powerRollup.power, massRollup.mass,
        efficiencyRollup.efficiency, costRollup.cost
        );
    }
    // The result of the analysis will be the alternative with either the maximum or minimum evaluated value.
    return part :>> selectedAlternative : Engine;
}
