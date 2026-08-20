library package FailureModelingMetadata {
    private import FailureModeling::*;
    private import Metaobjects::SemanticMetadata;
    // Declare semantic metadata for each concept to be included in the language extension.
    metadata def situation :> SemanticMetadata {
        // Bind baseType to the base usage for the relevant concept.
        :>> baseType = situations meta SysML::Usage;
    }
    metadata def cause :> SemanticMetadata {
        :>> baseType = causes meta SysML::Usage;
    }
    metadata def failure :> SemanticMetadata {
        // The meta-cast "meta SysML::Usage" allows failures to be referenced as a usage, rather than evaluated as an expression.
        :>> baseType = failures meta SysML::Usage;
    }
    metadata def causation :> SemanticMetadata {
        :>> baseType = causations meta SysML::Usage;
    }
    metadata def scenario :> SemanticMetadata {
        :>> baseType = scenarios meta SysML::Usage;
    }
}
