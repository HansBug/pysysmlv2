// A trade-off study is an analysis with the objective of selecting the optimum alternative from a given set based on an evaluation of each alternative.
analysis engineTradeStudy : TradeStudies::TradeStudy {
    subject : Engine = (engine4cyl, engine6cyl);
    objective : MaximizeObjective;
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
    return part :>> selectedAlternative : Engine;
}
