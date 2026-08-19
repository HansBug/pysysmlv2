// An individual definition is an occurrence definition (of any kind) restricted to model a single individual and how it changes over its lifetime.
// An individual definition will often specialize a definition of the general class of things the individual is one of.
individual part def Vehicle_1 :> Vehicle {
    // As occurrences, individuals can have snapshots that describe them at a single instant of time.
    snapshot part vehicle_1_t0 : Vehicle_1 {
        // This is a compact notation for showing redefinition of an attribute usage.
        :>> mass = 2000.0;
        // An attribute does not have snapshots, but it can be asserted to have a specific value in a certain snapshot.
        :>> status {
            :>> gearSetting = 0;
            :>> acceleratorPosition = 0.0;
        }
    }
}
