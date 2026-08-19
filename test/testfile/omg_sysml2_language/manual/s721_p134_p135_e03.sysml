requirement def BrakingRequirement {
    subject vehicle : Vehicle;
    actor environment : 'Driving Environment';
    stakeholder driver : Person;

    attribute speedLimit : SpeedValue;
    attribute maxBrakingDistance : DistanceValue;

    assume constraint {
        doc /* The environment conditions are poor. */
    }
    assume constraint {
        doc /* The driver is an occupant of the vehicle. */
    }
    assume constraint {
        doc /* The vehicle speed is less than the speed limit. */
    }

    require constraint {
        doc /* The vehicle shall brake from its initial speed to zero
             * speed in a distance less than the maxBrakingDistance.
             */
    }
}
