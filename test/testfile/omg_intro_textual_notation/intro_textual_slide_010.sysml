// An abstract definition is one whose instances must be members of some specialization.
abstract part def Vehicle;
// A specialized definition defines a subset of the classification of its generalization.
part def HumanDrivenVehicle specializes Vehicle {
    ref part driver : Person;
}
// The :> symbol is equivalent to the specializes keyword.
part def PoweredVehicle :> Vehicle {
    // A specialization can define additional features.
    part eng : Engine;
}
// A definition can have multiple generalizations, inheriting the features of all general definitions.
part def HumanDrivenPoweredVehicle :>
HumanDrivenVehicle, PoweredVehicle;
part def Engine;
part def Person;
