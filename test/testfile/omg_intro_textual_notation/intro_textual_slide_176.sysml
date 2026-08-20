// Generic time scale to express a time instant.
attribute def TimeScale :> IntervalScale {
    attribute :>> unit: DurationUnit[1];
    // Captures the specification of the time instant with value zero, also known as the (reference) epoch.
    attribute definitionalEpoch: DefinitionalQuantityValue[1];
    attribute :>> definitionalQuantityValues = definitionalEpoch;
}
// Representation of a time instant quantity.
attribute def TimeInstantValue :> ScalarQuantityValue {
    attribute :>> num: Real[1];
    attribute :>> mRef: TimeScale[1];
}
// Generic representation of a time instant as a calendar date and time of day.
attribute timeInstant: TimeInstantValue :> scalarQuantities;
abstract attribute def DateTime :> TimeInstantValue;
abstract attribute def Date :> TimeInstantValue;
abstract attribute def TimeOfDay :> TimeInstantValue;
// Coordinated Universal Time (UTC) time scale.
attribute UTC: TimeScale {
    attribute :>> longName = "Coordinated Universal Time";
    attribute :>> unit = SI::s;
    attribute :>> definitionalEpoch: DefinitionalQuantityValue {
        :>> num = 0;
        :>> definition = "UTC epoch at 1 January 1958 at 0 hour 0 minute 0 second";
    }
}
attribute def UtcTimeInstantValue :> DateTime { :>> mRef = UTC; }
attribute utcTimeInstant: UtcTimeInstantValue;
