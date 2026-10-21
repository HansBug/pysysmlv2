part def P specializes Parts::Part {
    // PortUsages not nested in PortDefinitions or PortUsages
    // are always referential (ref keyword is optional).
    ref port p : Pd subsets Parts::Part::ownedPorts;
}
