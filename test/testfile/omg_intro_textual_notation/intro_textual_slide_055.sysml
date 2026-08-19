// If no localClock is declared, the default is a universalClock that provides a common time universal reference.
part def Server {
    // Redefining the localClock feature of a part provides a local time reference for composite items, parts and actions nested within it.
    // Each Server instance will have its own independent Clock.
    part :>> localClock = new Time::Clock();
    attribute today : String;
    port requestPort;
    state ServerBehavior {
        first start then off;
        state off;
        // A localClock can also be declared for an item or an action (or any kind of occurrence that happens over time).
        accept Start via requestPort
        then waiting;
        state waiting;
        accept request : Request via requestPort
        then responding;
        // All absolute and relative time references are relative to the localClock.
        accept at new Time::Iso8601DateTime(today + "11:59:00")
        then off;
        state responding;
        accept after 5 [SI::min]
        then waiting;
    }
}
