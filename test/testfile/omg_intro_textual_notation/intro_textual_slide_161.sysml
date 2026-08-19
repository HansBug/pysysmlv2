standard library package DerivationConnections {
    // Specializations add ends for specific original and derived requirements.
    requirement originalRequirements[*];
    requirement derivedRequirements[*];
    // A connection between one original requirement and one or more derived requirements.
    abstract connection def Derivation {
        ref requirement originalRequirement[1]
        :>> originalRequirements :> participant;
        ref requirement :>> derivedRequirements[1..*]
        :> participant;
        // The original requirement must not be a derived requirement.
        private assert constraint originalNotDerived { ... }
        // Whenever the original requirement is satisfied, all derived requirements must be satisfied.
        private assert constraint originalImpliesDerived { ... }
    }
    abstract connection derivations : Derivation[*];
}
