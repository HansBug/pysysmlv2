metadata def Safety {
    attribute isMandatory : Boolean;
}
part vehicle {
    part interior {
        part alarm;
        part seatBelt[2] {
            // Currently, a metadata annotation must be owned by the annotated element to be accessed in a filter condition.
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
    // A recursive import (using **) imports members of a namespace and, recursively, members of any nested namespaces.
    public import vehicle::**;
    // A filter is a Boolean condition that must be true for an element to actually be imported into a package.
    filter @Safety;
}

package 'Mandatory Safety Features' {
    public import vehicle::**;
    // @ checks life an element has the given metadata and as “casts” to that metadata type.
    filter @Safety and (as Safety).isMandatory;
}
