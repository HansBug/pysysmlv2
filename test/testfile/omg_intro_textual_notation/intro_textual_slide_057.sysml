// An occurrence is something that happens over time. Items and parts are structural occurrences. Actions are behavioral occurrences. Attributes are not occurrences.
attribute def Date;
item def Person;
part def Vehicle {
    // A time slice represents a portion of the lifetime of an occurrence over some period of time.
    timeslice assembly;
    // A succession asserts that the first occurrence ends before the second can begin.
    first assembly then delivery;
    // A snapshot represents an occurrence at a specific point in time (a time slice with zero duration).
    snapshot delivery;
    first delivery then ownership;
    timeslice ownership[0..*] ordered;
    // done is the name of the end-of-life snapshot of any occurrence.
    snapshot junked = done;
}
