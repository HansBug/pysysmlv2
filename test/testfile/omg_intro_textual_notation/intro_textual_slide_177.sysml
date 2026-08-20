// Representation of an ISO 8601-1 date and time in extended string format.
attribute def Iso8601DateTimeEncoding :> String;
// Representation of an ISO 8601 date and time with explicit date and time component attributes.
attribute def Iso8601DateTime :> UtcTimeInstantValue {
    attribute :>> num = getElapsedUtcTime(val);
    attribute val: Iso8601DateTimeEncoding;
    private calc getElapsedUtcTime
    {in iso8601DateTime: Iso8601DateTimeEncoding; return : Real;}
}
attribute def Iso8601DateTimeStructure :> UtcTimeInstantValue {
    attribute :>> num = getElapsedUtcTime(year, month, day, hour, minute, second,
    microsecond, hourOffset, minuteOffest);
    attribute :>> mRef = UTC;
    attribute year: Integer;
    attribute month: Natural;
    attribute day: Natural;
    attribute hour: Natural;
    attribute minute: Natural;
    attribute second: Natural;
    attribute microsecond: Natural;
    attribute hourOffset: Integer;
    attribute minuteOffest: Integer;
    private calc getElapsedUtcTime(year: Integer, month: Natural, day: Natural,
    hour: Natural, minute: Natural, second: Natural, microsecond: Natural,
    hourOffset: Integer, minuteOffest: Integer) : Real;
}
...
}
