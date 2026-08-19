// A calculation definition is a reusable, parameterized expression.
calc def Power {
    // Similarly to actions, the directed features of a calculation are its parameters.
    in whlpwr : PowerValue;
    in Cd : Real;
    in Cf : Real;
    in tm : MassValue;
    in v : SpeedValue;
    // A calculation has a single return result.
    return : PowerValue;
    // The calculation can include the computation of intermediate values.
    attribute drag = Cd * v;
    attribute friction = Cf * tm * v;
    // The calculation result expression must conform to the return type.
    whlpwr - drag - friction
}
calc def Acceleration { in tp: PowerValue; in tm : MassValue; in v: SpeedValue;
    // The result expression can also be bound directly to the return parameter.
    return : AccelerationValue = tp / (tm * v);
}
calc def Velocity { in dt : TimeValue; in v0 : SpeedValue; in a : AccelValue;
    return : SpeedValue = v0 + a * dt;
}

calc def Position (dt : TimeValue; x0 : LengthValue; v : SpeedValue;
return : LengthValue = x0 + v * dt;
}
