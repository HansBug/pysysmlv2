...
// ContinuousStateSpaceDynamics represents continuous behavior. The derivative needs to return a time derivative of stateSpace, i.e. dx/dt.
abstract action def ContinuousStateSpaceDynamics :> StateSpaceDynamics {
    abstract calc getDerivative: GetDerivative;
    calc :>> getNextState: GetNextState {
        calc integrate: Integrate {
            in derivative = ContinuousStateSpaceDynamics::getDerivative;
            in input = GetNextState::input;
            in initialState = GetNextState::stateSpace;
            in timeInterval = GetNextState::timeStep;
            return resultState = result;
        }
    }
    event occurrence zeroCrossingEvents[0..*] : ZeroCrossingEventDef;
}
abstract calc def GetDifference {
    in input: Input; in stateSpace: StateSpace;
    return : StateSpace;}
// DiscreteStateSpaceDynamics represents discrete behavior. getDifference returns the difference of the stateSpace for each timestep.
abstract action def DiscreteStateSpaceDynamics :> StateSpaceDynamics {
    abstract calc getifference: GetDifference;
    calc :>> getNextState: GetNextState {
        attribute diff: StateSpace = getDifference(input, stateSpace);
        stateSpace + diff
    }
}
}
