// An item definition defines a class of things that exist in space and time but are not necessarily considered "parts" of a system being modeled.
item def Fuel;
item def Person;
// All parts can be treated as items, but not all items are parts. The design of a system determines what should be modeled as its "parts".
part def Vehicle {
    // The default multiplicity for attributes and items is also 1..1.
    attribute mass : Real;
    // A system model may reference discrete items that interact with or pass through the system.
    ref item driver : Person;
    part fuelTank {
        // Items may also model continuous materials that are stored in and/or flow between parts of a system.
        // An item is continuous if any portion of it in space is the same kind of thing. A portion of fuel is still fuel. A portion of a person is generally no longer a person.
        item fuel: Fuel;
    }
}
