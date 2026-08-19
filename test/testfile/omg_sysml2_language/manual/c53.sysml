part def LogicalSystem {
  part component : LogicalComponent;
}
part def PhysicalDevice {
  part assembly : PhysicalAssembly;
}
allocation def LogicalToPhysicalAllocation {
  end part logical : LogicalSystem;
  end part physical : PhysicalDevice;

  // This is a nested sub-allocation.
  allocate logical.component to physical.assembly;
}
part system : LogicalSystem;
part device : PhysicalDevice;
allocation systemToDevice : LogicalToPhysicalAllocation
  allocate logical ::> system to physical ::> device;
