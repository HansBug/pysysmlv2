standard library package TradeStudies {
    private import Base::Anything;
    private import ScalarValues::*;
    private import ScalarFunctions::*;
    // An EvaluationFunction is a calculation that evaluates a TradeStudy alternative.
    abstract calc def EvaluationFunction(alternative) result : ScalarValue[1];
    // A TradeStudyObjective is the base definition for the objective of a TradeStudy, requiring the selectedAlternative to have best evaluation according to a given EvaluationFunction.
    abstract requirement def TradeStudyObjective {
        subject selectedAlternative : Anything;
        in ref alternatives : Anything[1..*];
        in calc eval : EvaluationFunction;
        out attribute best : ScalarValue;
        require constraint { eval(selectedAlternative) == best }
    }
    requirement def MinimizeObjective :> TradeStudyObjective {
        ...
        attribute :>> best = alternatives->minimize {in x; eval(x)};
    }
    requirement def MaximizeObjective :> TradeStudyObjective {
        ...
        attribute :>> best = alternatives->maximize {in x; eval(x)};
    }
    // A TradeStudy is an analysis case whose subject is a set of alternatives and whose result is a selection of one of those alternatives, based on a given EvaluationFunction such that it satisfies the objective of the TradeStudy.
    abstract analysis def TradeStudy {
        subject studyAlternatives : Anything[1..*];
        abstract calc evaluationFunction : EvaluationFunction;
        objective tradeStudyObjective : TradeStudyObjective {
            subject :>> selectedAlternative;
            in ref :>> alternatives = studyAlternatives;
            in calc :>> eval = evaluationFunction;
        }
        return selectedAlternative : Anything =
        studyAlternatives->selectOne {in ref a; tradeStudyObjective(selectedAlternative = a)};
    }
