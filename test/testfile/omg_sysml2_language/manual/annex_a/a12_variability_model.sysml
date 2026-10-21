variation part def TransmissionChoices :> Transmission {
    variant part transmissionAutomatic : TransmissionAutomatic;
    variant part transmissionManual : TransmissionManual;
}
abstract part vehicleFamily :> vehicle_a {
    variation part engine : Engine {
        variant part engine4Cyl : Engine4Cyl;
        variant part engine6Cyl : Engine6Cyl {
            part cylinder : Cylinder [6] {
                variation attribute diameter : LengthValue {
                    variant attribute smallDiameter : LengthValue;
                    variant attribute largeDiagmeter : LengthValue;
                }
            }
        }
    }
    variation part transmission : TransmissionChoices;
    variation part sunroof : Sunroof;
    assert constraint selectionConstraint {
        (engine == engine::engine4Cyl and
            transmission == TransmissionChoices::transmissionManual) xor
        (engine == engine::engine6Cyl and
            transmission == TransmissionChoices::transmissionAutomatic)
    }
}
