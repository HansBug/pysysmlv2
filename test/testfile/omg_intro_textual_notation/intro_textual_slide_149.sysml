standard library package ParametersOfInterestMetadata {
    private import Metaobjects::SemanticMetadata;
    // Semantic metadata for identifying an attribute as a measure of effectiveness.
    attribute measuresOfEffectiveness[*] nonunique;
    // Semantic metadata for identifying an attribute as a measure of performance.
    attribute measuresOfPerformance[*] nonunique;
    metadata def <moe> MeasureOfEffectiveness :> SemanticMetadata {
        :>> annotatedElement : SysML::Usage;
        :>> baseType = measuresOfEffectiveness meta SysML::Usage;
    }
    metadata def <mop> MeasureOfPerformance :> SemanticMetadata {
        :>> annotatedElement : SysML::Usage;
        :>> baseType = measuresOfPerformance meta SysML::Usage;
    }
}
