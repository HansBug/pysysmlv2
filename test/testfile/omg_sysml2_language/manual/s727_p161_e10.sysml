occurrence def Situation;
occurrence situations : Situation[0..*] nonunique;

// It is often convenient to use a lower-case initial name or
// short name for semantic metadata intended to be used as a keyword.
metadata def <situation> SituationMetadata :> SemanticMetadata {
    :>> baseType = situations meta SysML::Usage;
}

// Failure is an OccurrenceDefinition that implicitly subclassifies Situation.
#situation occurrence def Failure;

// batteryLow is an OccurrenceUsage that implicitly subsets situations.
#situation occurrence batteryLow;
