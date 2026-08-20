// For a domain-specific extension to SysML, first create a library model of domain-specific concepts. This can be explicitly identified as a library package.
library package FailureModeling {
    // For each concept, provide a base definition and a base usage modeling the concept semantics.
    abstract occurrence def Situation;
    abstract occurrence situations : Situation[*] nonunique;
    abstract occurrence def Cause {
        attribute probability : Real;
    }
    abstract occurrence causes : Cause[*] nonunique :> situations;
    abstract occurrence def Failure {
        attribute severity : Level;
    }
    abstract occurrence failures : Failure[*] nonunique :> situations;
    // HappensBefore is the base type for successions, from the Kernel Library Occurrences package.
    abstract connection def Causation :> Occurrences::HappensBefore {
        end cause : Situation[*];
        end effect : Situation[*];
    }
    abstract connection causations : Causation[*] nonunique;
    item def Scenario {
        occurrence :>> situations;
        occurrence :>> causes :> situations;
        occurrence :>> failures :> situations;
    }
    item scenarios : Scenario[*] nonunique;
}
