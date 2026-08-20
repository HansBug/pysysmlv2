analysis engineTradeStudy : TradeStudy {
    // The subject is bound to the two alternatives to be studied.
    subject : Engine = (engine4cyl, engine6cyl);

    // The objective is to find the alternative that has the
    // maximum value for the evaluationFunction.
    objective : MaximizeObjective;

    // For each one of the alternatives, the evaluationFunction
    // produces a numerical evaluation result.
    calc :>> evaluationFunction {
        in part anEngine : Engine :>> alternative;

        calc powerRollup: PowerRollup {
            in engine = anEngine;
            return power;
        }
        calc massRollup: MassRollup {
            in engine = anEngine;
            return mass;
        }
        calc efficiencyRollup: EfficiencyRollup {
            in engine = anEngine;
            return efficiency;
        }
        calc costRollup: CostRollup {
            in engine = anEngine;
            return cost;
        }

        return :>> result : Real = EngineEvaluation(
            power = powerRollup.power,
            mass = massRollup.mass,
            efficiency = efficiencyRollup.efficiency,
            cost = costRollup.cost
        );
    }

    // The selected alternative will be the one that has the
    // maximum value for the evaluationFunction.
    return part :>> selectedAlternative : Engine;
}
