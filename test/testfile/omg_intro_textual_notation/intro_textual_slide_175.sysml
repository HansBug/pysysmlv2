standard library package Time {
    // A singleton universal time reference.
    part universalClock : Clock[1] :>
    Clocks::universalClock;
    // Clocks is a Kernel Library model of the semantics of clocks.
    part def Clock :> Clocks::Clock {
        // A clock provides the current time as a quantity that advances monotonically over the lifetime of the clock.
        attribute :>> currentTime : TimeInstantValue;
    }
    // TimeOf returns the time instant of the start of an occurrence relative to a given clock.
    calc def TimeOf :> Clocks::TimeOf {
        in o : Occurrence[1];
        in clock : Clock[1] default localClock;
        return timeInstant : TimeInstantValue[1];
    }
    // DurationOf returns the duration of a given occurrence relative to a given clock (the time of its end snapshot minus the time of its start snapshot).
    calc def DurationOf :> Clocks::DurationOf {
        in o : Occurrence[1];
        in clock : Clock[1] default localClock;
        return duration : DurationValue;
    }
