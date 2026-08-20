standard library package SpatialItems {
    ...
    // A spatial item is an Item with a three-dimensional spatial extent that also acts as a spatial frame of reference.
    item def SpatialItem :> SpatialFrame {
        item :>> self : SpatialItem;
        item :>> localClock : Clock[1] default Time::universalClock;
        // A spatial item has local time and space references used within it.
        attribute coordinateFrame : ThreeDCoordinateFrame[1]
        default universalCartesianSpatial3dCoordinateFrame;
        item originPoint : Point[1] :> spaceShots;
        item subSpatialItems : SpatialItem[1..*] :> subitems {
            ref item :>> SpatialItem::localClock, subitems::localClock;
        }
        item componentItems : SpatialItem[0..*] ordered :> subSpatialItems {
            ref item :>> SpatialItem::localClock, subSpatialItems::localClock;
            attribute :>> coordinateFrame {
                attribute :>> transformation[1] default nullTransformation { ... }
            }
        }
        private attribute cunionNum: Natural [1] = if isEmpty(componentItems) ? 0 else 1;
        private attribute componentUnion[cunionNum] :> unionsOf {
            // A compound spatial item is a spatial item that is a (spatial) union of a collection of component spatial items.
            item :>> elements : SpatialItem[1..*] = componentItems;
        }
        ...
    }
    ...
}
