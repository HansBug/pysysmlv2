// A part definition is a definition of a class of systems or parts of systems, which are mutable and exist in space and time.
part def Vehicle {
    // An attribute usage usage of an attribute definition, used here as a feature of the part definition.
    attribute mass : ScalarValues::Real;
    // A part usage is a composite feature that is the usage of a part definition.
    part eng : Engine;
    // A reference part usage is a referential feature that is the usage of a part definition.
    ref part driver : Person;
}
// An attribute definition is a definition of attributive data that can be used to describe systems or parts.
attribute def VehicleStatus {
    // Definitions and usages are also namespaces that allow import.
    private import ScalarValues::*;
    // An attribute definition may not have composite features. Attribute usages are always referential.
    attribute gearSetting : Integer;
    attribute acceleratorPosition : Real;
}
part def Engine;
part def Person;
