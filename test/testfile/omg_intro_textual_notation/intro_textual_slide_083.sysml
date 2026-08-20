// In UML and SysML v1, constraints are often used to define derived values.
part vehicle1 : Vehicle {
    attribute totalMass : MassValue;
    assert constraint {totalMass == chassisMass + engine.mass + transmission.mass}
}
part vehicle2 : Vehicle {
    // In SysML v2 this can usually be done more directly using a binding.
    attribute totalMass : MassValue = chassisMass + engine.mass + transmission.mass;
}
constraint def AveragedDynamics {
    in mass: MassValue;
    in initialSpeed : SpeedValue;
    in finalSpeed : SpeedValue;
    in deltaT : TimeValue;
    in force : ForceValue;
    // However, constraints allow for more general equalities and inequalities than direct derivation.
    // Be careful about the difference between ==, which is the Boolean-valued equality operator, and =, which denotes binding.
    force * deltaT == mass * (finalSpeed - initialSpeed) and
    mass > 0[kg]
}
