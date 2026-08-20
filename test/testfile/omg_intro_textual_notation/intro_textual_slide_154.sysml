standard library package StateSpaceRepresentation {
    private import ISQ::DurationValue;
    private import Quantities::VectorQuantityValue;
    private import VectorCalculations::*;
    abstract attribute def StateSpace :> VectorQuantityValue;
    abstract attribute def Input :> VectorQuantityValue;
    abstract attribute def Output :> VectorQuantityValue;
    abstract calc def GetNextState
    {in input: Input; in stateSpace: StateSpace; in timeStep: DurationValue; return : StateSpace;}
    abstract calc def GetOutput
    {in input: Input; in stateSpace: StateSpace; return : Output;}
    abstract action def StateSpaceEventDef;
    action def ZeroCrossingEventDef :> StateSpaceEventDef;
    item def StateSpaceItem;
    // StateSpaceDynamics is the simplest form of state space representation, and getNextState directly computes the stateSpace of the next timestep.
    abstract action def StateSpaceDynamics {
        in attribute input: Input;
        abstract calc getNextState: GetNextState;
        abstract calc getOutput: GetOutput;
        attribute stateSpace: StateSpace;
        out attribute output: Output = getOutput(input, stateSpace);
    }
    abstract attribute def StateDerivative :> VectorQuantityValue { ... }
    abstract calc def GetDerivative
    {in input: Input; in stateSpace: StateSpace; return : StateDerivative;}
    abstract calc def Integrate {in getDerivative: GetDerivative; in input: Input;
        in initialState: StateSpace; in timeInterval: DurationValue; return result: StateSpace;}
    ...
