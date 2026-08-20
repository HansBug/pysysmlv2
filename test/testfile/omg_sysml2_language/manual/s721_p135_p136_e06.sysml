requirement def BrakingRequirement {
    subject vehicle : Vehicle;
    actor environment : 'Driving Environment';

    attribute speedLimit : SpeedValue;
    attribute maxBrakingDistance : DistanceValue;

    assume constraint {
        doc /* The environment conditions are poor. */
    }

    frame concern brakingConcern : BrakingConcern {
        // Subject is automatically bound to "vehicle".
        :>> maxBrakingDistance = BrakingRequirement::maxBrakingDistance;
    }
}
