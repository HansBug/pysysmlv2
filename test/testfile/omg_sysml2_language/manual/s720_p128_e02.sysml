part testObject {
    attribute computedMass : MassValue;
    assert constraint { computedMass >= 0[kg] }
    // Alternatively, the following is equivalent.
    assert not constraint { computedMass < 0[kg] }
}
