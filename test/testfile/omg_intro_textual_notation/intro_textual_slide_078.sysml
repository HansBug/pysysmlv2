attribute def DynamicState {
    attribute v: SpeedValue;
    attribute x: LengthValue;
}
part def VehicleDynamics {
    attribute C_d : Real;
    attribute C_f : Real;
    attribute wheelPower : PowerValue;
    attribute mass : MassValue;

    // A calculation can be specified without an explicit calculation definition.
    calc updateState {
        in delta_t : TimeValue; in currState : DynamicState;
        attribute totalPower : PowerValue =
        Power(wheelPower, C_d, C_f, mass, currState.v);
        // Calculations can also handle structured values.
        // This is a declaration of the result parameter of the calculation, with bound subattributes.
        return attribute newState : DynamicState {
            :>> v = Velocity(delta_t, currState.v, Acceleration(totalPower, mass, currState.v));
            :>> x = Position(delta_t, currState.x, currState.v);
        }
    }
}
