// An enumeration definition is a kind of attribute definition that defines a set of enumerated values.
enum def TrafficLightColor {
    enum green;
    enum yellow;
    enum red;
}
part def TrafficLight {
    // The values of an attribute usage defined by an enumeration definition are limited to the defined set of enumerated values.
    attribute currentColor : TrafficLightColor;
}
part def TrafficLightGo specializes TrafficLight {
    // This shows an attribute being bound to a specific value (more on binding later).
    attribute redefines currentColor = TrafficLightColor::green;
}
