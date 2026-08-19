action def ChangeAircraft {
    in flight : Flight;
    in newAircraft : Aircraft;
    // This assignment changes the aircraft for the given flight.
    assign flight.aircraft := newAircraft;
}
