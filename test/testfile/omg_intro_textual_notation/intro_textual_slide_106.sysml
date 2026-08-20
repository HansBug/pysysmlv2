package LogicalModel {
    ...
    part torqueGenerator : TorqueGenerator {
        perform generateTorque;
    }
}
package PhysicalModel {
    private import LogicalModel::*;
    ...
    part powerTrain : PowerTrain {
        part engine : Engine {
            perform generateTorque;
        }
    }
    // An allocation specifies that some or all of the responsibility for realizing the intent of the source is allocated to the target.
    // Allocations define traceable links across the various structures and hierarchies of a system model, perhaps as a precursor to more rigorous specifications and implementations.
    allocate torqueGenerator to powerTrain {
        // An allocation can be refined using nested allocations that give a finer-grained decomposition of the containing allocation mapping.
        allocate torqueGenerator.generateTorque
            to powerTrain.engine.generateTorque;
    }
}
