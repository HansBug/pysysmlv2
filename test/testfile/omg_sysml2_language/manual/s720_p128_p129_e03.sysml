constraint negativeMass {
    attribute mass : MassValue;
    mass < 0[kg]
}
part testObject {
    attribute computedMass : MassValue;

    // The following is equivalent to
    // assert not constraint references negativeMass { ... }
    assert not negativeMass {
        :>> mass = computedMass;
    }
}
part alienObject {
    attribute antiMass : MassValue;

    // The following is equivalent to
    // assert constraint references negativeMass { ... }
    assert negativeMass {
        :>> mass = antiMass;
    }
}
