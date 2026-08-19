package LogicalModel {
    ...
    part def LogicalElement;
    part def TorqueGenerator :> LogicalElement;
    part torqueGenerator : TorqueGenerator { ... }
}
package PhysicalModel {
    private import LogicalModel::*;
    ...
    part def PhysicalElement;
    part def PowerTrain :> PhysicalElement;
    part powerTrain : PowerTrain { ... }
}
// An allocation definition defines a class of allocations between features of specific types.
allocation def LogicalToPhysical {
    end logical : LogicalElement;
    end physical : PhysicalElement;
}
// An allocation usage must allocate features that conform to the types of the ends of its allocation definition.
allocation torqueGenAlloc : LogicalToPhysical
allocate torqueGenerator to powerTrain { ... }
}
