standard library package SpatialItems {
    ...
    // The position of points in space can be determined relative to the space and time references of a spatial item.
    calc def PositionOf :> SpatialFrames::PositionOf {
        in point : Point[1];
        in timeInstant : TimeInstantValue[1];
        in enclosingItem :>> 'frame' : SpatialItem[1];
        in clock : Clock[1] default enclosingItem.localClock;
        return positionVector : VectorQuantityValue[1];
    }
    // The position of a point can move over time, with its "current" position being relative to the clock reference of the spatial item.
    calc def CurrentPositionOf :> SpatialFrames::CurrentPositionOf {
        in point : Point[1];
        in enclosingItem :>> 'frame' : SpatialItem[1];
        in clock : Clock[1] default enclosingItem.localClock;
        return positionVector : VectorQuantityValue[1];
    }
    calc def DisplacementOf :> SpatialFrames::DisplacementOf {
        in point1 : Point[1];
        in point2 : Point[1];
        in timeInstant : TimeInstantValue[1];
        in spacialItem :>> 'frame' : SpatialItem[1];
        in clock : Clock[1] default spacialItem.localClock;
        return displacementVector : VectorQuantityValue[1];
    }
    calc def CurrentDisplacementOf :> SpatialFrames::CurrentDisplacementOf {
        in point1 : Point[1];
        in point2 : Point[1];
        in spacialItem :>> 'frame' : SpatialItem[1];
        in clock : Clock[1] default spacialItem.localClock;
        return displacementVector : VectorQuantityValue[1];
    }
}
