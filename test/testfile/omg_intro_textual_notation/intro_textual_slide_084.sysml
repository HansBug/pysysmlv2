// This constraint definition provides a reusable specification of a system of (coupled) equations.
constraint def StraightLineDynamicsEquations {
    in p : PowerValue, in m : MassValue, in dt : TimeValue;
    in x_i : LengthValue; in v_i : SpeedValue;
    in x_f : LengthValue; in v_f : SpeedValue,
    in a : AccelerationValue;
    attribute v_avg : SpeedValue = (v_i + v_f)/2;
    // Note the use of the calculation definitions defined earlier.
    a == Acceleration(p, m, v_avg) and
    v_f == Velocity(dt, v_i, a) and
    x_f == Position(dt, x_i, v_avg)
}
// An action definition is inherently "causal" in the sense that outputs are determined in terms of inputs.
action def StraightLineDynamics {
    in power : PowerValue; in mass : MassValue; in delta_t : TimeValue;
    in x_in : LengthValue; in v_in : SpeedValue;
    out x_out : LengthValue; out v_out : SpeedValue;
    out a_out : AccelerationValue;
    // A constraint is inherently "acausal" – it is simply true or false for given values of its parameters.
    assert constraint dynamics : StraightLineDynamicsEquations {
        // This specifies that the action outputs must be solved for analytically given the action inputs, consistent with the asserted constraint.
        in p = power; in m = mass; in dt = delta_t;
        in x_i = x_in; in v_i = v_in;
        in x_f = x_out; in v_f = v_out;
        in a = a_out;
    }
}
