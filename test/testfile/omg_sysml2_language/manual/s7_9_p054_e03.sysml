occurrence def ApprovedFlight :> Flight {
    // This redefines the aircraft feature so it is constant for
    // an entire ApprovedFlight.
    constant ref part approvedAircraft redefines aircraft;
}
