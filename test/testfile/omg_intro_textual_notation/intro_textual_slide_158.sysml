standard library package CausationConnections {
    abstract occurrence causes[*];
    abstract occurrence effects[*];
    // A connection between one or more cause occurrences and one or more effect occurrences. Specializations add ends for specific causes and effects.
    abstract connection def Multicausation {
        abstract constant ref occurrence causes[1..*]
        :>> causes :> participant;
        abstract constant ref occurrence effects[1..*]
        :>> effects :> participant;
        ...
    }
    abstract connection multicausations : Multicausation[*] {
        // A binary connection between a single cause and a single effect. (But a single cause can separately have multiple effects, and a single effect can separately have multiple causes.)
        connection def Causation :> Multicausation {
            end theCauses[*] occurrence theCause
            :>> causes :>> source;
            end theEffects[*] occurrence theEffect
            :>> effects :>> target;
        }
        abstract connection causations : Causation[*]
        :> multicausations;
    }
