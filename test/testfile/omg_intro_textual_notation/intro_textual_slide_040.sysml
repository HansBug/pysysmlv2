action def Brake {
    action turnOn;
    // A fork node enables all its successors to happen after it.
    // The source for all these successions is the fork node.
    then fork;
    then monitorBrakePedal;
    then monitorTraction;
    then braking;
    action monitorBrakePedal : MonitorBrakePedal {
        out brakePressure; }
    then joinNode;
    action monitorTraction : MonitorTraction {
        out modulationFrequency; }
    then joinNode;
    flow monitorBrakePedal.brakePressure to
    braking.breakPressure;
    flow monitorTraction.modulationFrequency to
    braking.modulationFrequency;
    action braking : Braking {
        in brakePressure;
        in modulationFrequency; }
    then joinNode;
    // A join node waits for all its predecessors to happen before continuing.
    join joinNode;
    then done;
}
