requirement <'v1.1'> vehicleMaximumMass : MaximumMass {
    doc
    /* The total mass of a Vehicle shall be no greater than
     * its required mass.
     */

    subject vehicle : Vehicle;
    attribute :>> massActual = vehicle.totalMass;
    attribute :>> massRequired = 2000[kg];
    // Required and assumed constraints are inherited.
}
