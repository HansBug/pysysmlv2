requirement def <'1.1'> MaximumMass {
    doc
    /*
     * Assuming the required mass is greater than 0,
     * the actual mass shall be less than or equal to
     * the required mass.
     */

    attribute massActual : MassValue;
    attribute massRequired : MassValue;
    assume constraint { massRequired > 0[kg] }
    require constraint { massActual <= massRequired }
}
