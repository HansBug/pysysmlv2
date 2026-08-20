// Metadata is additional data that can be used to annotate the elements of a model.
part vehicle {
    part interior {
        part alarm;
        part seatBelt[2];
        part frontSeat[2];
        part driverAirBag;
    }
    part bodyAssy {
        part body;
        part bumper;
        part keylessEntry;
    }
}
// Metadata is defined using a metadata definition.
metadata def SafetyFeature;
// The KerML and SysML library models include all the metaclasses from the KerML and SysML abstract syntax.
metadata def SecurityFeature {
    // To restrict what kind of element can be annotated, subset the annotatedElement feature with the desired element type(s).
    :> annotatedElement : SysML::PartDefinition;
    :> annotatedElement : SysML::PartUsage;
}
// A specific type of metadata can then be applied as an annotation to one or more model elements.
metadata SafetyFeature about
vehicle::interior::seatBelt,
vehicle::interior::driverAirBag,
vehicle::bodyAssy::bumper;
// At its simplest, a metadata annotation can be used to simply "tag" certain elements, so that they can, e.g., be grouped by tooling.
metadata SecurityFeature about
vehicle::interior::alarm,
vehicle::bodyAssy::keylessEntry;
