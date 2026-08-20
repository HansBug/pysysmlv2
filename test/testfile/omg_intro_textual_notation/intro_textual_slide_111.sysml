metadata def Safety {
    attribute isMandatory : Boolean;
}
part vehicle {
    part interior {
        part alarm;
        part seatBelt[2] {
            @Safety { isMandatory = true; }
        }
        part frontSeat[2];
        part driverAirBag {
            @Safety { isMandatory = false; }
        }
    }
    part bodyAssy {
        part body;
        part bumper {
            @Safety { isMandatory = true; }
        }
        part keylessEntry;
    }
    part wheelAssy {
        part wheel[2];
        part antilockBrakes[2] {
            @Safety { isMandatory = false; }
        }
    }
}

package 'Safety Features' {
    // The filter keyword is only allowed in a package (or view), but a filtered import can be used anyplace an import is allowed.
    public import vehicle::**[@Safety];
}

package 'Mandatory Safety Features' {
    // Filter conditions can also be combined with the import itself.
    // A filter condition expression must be model-level evaluable. It can reference only literals and metadata annotations and attributes, connected using basic arithmetic, comparison and Boolean operators.
    public import vehicle::**[@Safety and (as Safety).isMandatory];
}
