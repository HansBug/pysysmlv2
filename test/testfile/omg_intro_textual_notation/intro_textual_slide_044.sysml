action def ComputeMotion {
    in attribute powerProfile :> ISQ::power[*];
    in attribute vehicleMass :> ISQ::mass;
    in attribute initialPosition :> ISQ::length;
    in attribute initialSpeed :> ISQ::speed;
    in attribute deltaT :> ISQ::time;
    out attribute positions :> ISQ::length[*] := ( );
    // Using := instead of = here indicates an initial value, instead of a binding.
    private attribute position := initialPosition;
    private attribute speed := initialSpeed;
    // A for loop action repeatedly performs its body, setting a loop variable to successive values from the result of a sequence expression.
    for vehiclePower in powerProfile {
        // An action may also be performed by another action (similar to a "call").
        perform action dynamics : StraightLineDynamics {
            in power = vehiclePower;
            in mass = vehicleMass;
            in delta_t = deltaT;
            in x_in = position; in v_in = speed;
            out x_out; out v_out;
        }
        // An assignment action sets the value of a feature to the result of an expression at the time of performance of the assignment.
        then assign position := dynamics.x_out;
        then assign speed := dynamics.v_out;
        then assign positions :=
        // The functions including comes from the SequenceFunctions library package.
        positions->including(position);
    }
}
