standard library package CauseAndEffect {
    public import CausationConnections::*;
    private import ScalarValues::*;
    private import Metaobjects::SemanticMetadata;
    // Used to tag the "cause" ends of a multicausation.
    metadata def <cause> CauseMetadata :> SemanticMetadata {
        ref :>> annotatedElement : SysML::Usage;
        ref :>> baseType = causes meta SysML::Usage;
    }
    // Used to tag the "effect" ends of a multicausation.
    metadata def <effect> EffectMetadata :> SemanticMetadata {
        ref :>> annotatedElement : SysML::Usage;
        ref :>> baseType = effects meta SysML::Usage;
    }
    // Additional metadata about a causation connection.
    metadata def CausationMetadata {
        ref :> annotatedElement : SysML::ConnectionDefinition;
        ref :> annotatedElement : SysML::ConnectionUsage;
        attribute isNecessary : Boolean default false;
        attribute isSufficient : Boolean default false;
        attribute probability : Real[0..1];
    }
    // Semantic metadata for multicausation.
    metadata def <multicausation> MulticausationSemanticMetadata
    :> CausationMetadata, SemanticMetadata {
        ref :>> baseType = multicausations meta SysML::Usage;
    }
    // Semantic metadata for binary cauasation.
    metadata def <causation> CausationSemanticMetadadata
    :> CausationMetadata, SemanticMetadata {
        ref :>> baseType = causations meta SysML::Usage;
    }
}
