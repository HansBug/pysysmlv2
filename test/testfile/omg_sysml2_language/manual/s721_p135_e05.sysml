concern def BrakingConcern {
    subject vehicle : Vehicle;
    stakeholder driver : Person;

    attribute maxBrakingDistance : DistanceValue;

    assume constraint {
        doc /* The driver is an occupant of the vehicle. */
    }
    require constraint {
        doc /* The vehicle shall brake from its initial speed to zero
             * speed in a distance less than the maxBrakingDistance.
             */
    }
}
