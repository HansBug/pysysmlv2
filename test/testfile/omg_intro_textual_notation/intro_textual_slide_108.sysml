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
metadata def SecurityFeature {
    :> annotatedElement : SysML::PartDefinition;
    :> annotatedElement : SysML::PartUsage;
}
// A specific type of metadata can then be applied as an annotation to one or more model elements.
metadata SafetyFeature about
vehicle::interior::seatBelt,
vehicle::interior::driverAirBag,
vehicle::bodyAssy::bumper;
metadata SecurityFeature about
vehicle::interior::alarm,
vehicle::bodyAssy::keylessEntry;
