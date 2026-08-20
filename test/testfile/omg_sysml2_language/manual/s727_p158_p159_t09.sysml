state 'failure modes' [*];
metadata def <fm>
    'failure mode' :> SemanticMetadata {
    :>> baseType = 'failure modes' meta SysML::StateUsage;
    :> annotatedElement : SysML::StateDefinition;
    :> annotatedElement : SysML::StateUsage;
}
