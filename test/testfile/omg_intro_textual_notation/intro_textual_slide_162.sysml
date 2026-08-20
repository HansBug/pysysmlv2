standard library package RequirementDerivation {
    public import DerivationConnections::*;
    private import Metaobjects::SemanticMetadata;
    // Used to tag the "original" ends of a derivation.
    metadata def <original> OriginalRequirementMetadata
    :> SemanticMetadata {
        :> annotatedElement : SysML::Usage;
        :>> baseType = originalRequirements meta SysML::Usage;
    }
    // Used to tag the "derived" ends of a derivation.
    metadata def <derive> DerivedRequirementMetadata
    :> SemanticMetadata {
        :> annotatedElement : SysML::Usage;
        :>> baseType = derivedRequirements meta SysML::Usage;
    }
    // Semantic metadata for requirement derivation.
    metadata def <derivation> DerivationMetadata
    :> SemanticMetadata {
        :> annotatedElement : SysML::ConnectionDefinition;
        :> annotatedElement : SysML::ConnectionUsage;
        :>> baseType = derivations meta SysML::Usage;
    }
}
