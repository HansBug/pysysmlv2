library package FailureModelingMetadata {
    private import FailureModeling::*;
    private import Metaobjects::SemanticMetadata;
    // Declare semantic metadata for each concept to be included in the language extension.
    metadata def situation :> SemanticMetadata {
        :>> baseType = situations meta SysML::Usage;
    }
    metadata def cause :> SemanticMetadata {
        :>> baseType = causes meta SysML::Usage;
    }
    metadata def failure :> SemanticMetadata {
        :>> baseType = failures meta SysML::Usage;
    }
    metadata def causation :> SemanticMetadata {
        :>> baseType = causations meta SysML::Usage;
    }
    metadata def scenario :> SemanticMetadata {
        :>> baseType = scenarios meta SysML::Usage;
    }
}
