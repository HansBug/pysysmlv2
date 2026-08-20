attribute def ClassificationLevel {
    attribute code : String;
    attribute color : TrafficLightColor;
}
// An enumeration definition can contain nothing but declarations of its enumerated values. However, it can specialize a regular attribute definition and inherit nested features.
// An enumeration definition cannot specialize another enumeration definition.
enum def ClassificationKind specializes ClassificationLevel {
    // The enum keyword is optional when declaring enumerated values.
    unclassified {
        // The nested features can then be bound to specific values in each of the enumerated values.
        :>> code = "uncl";
        :>> color = TrafficLightColor::green;
    }
    confidential {
        :>> code = "conf";
        :>> color = TrafficLightColor::yellow;
    }
    secret {
        :>> code = "secr";
        :>> color = TrafficLightColor::red;
    }
}
enum def GradePoints :> Real {
    // Enumerated values can also be bound directly to specific values of a specialized attribute definition or data type.
    A = 4.0;
    B = 3.0;
    C = 2.0;
    D = 1.0;
    F = 0.0;
}
