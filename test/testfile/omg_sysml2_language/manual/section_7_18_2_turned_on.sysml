action monitorTemperature;
state def TurnedOn {
    entry;
    do monitorTemperature;
}
