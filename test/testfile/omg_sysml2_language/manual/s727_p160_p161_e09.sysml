action def UserAction;
action userActions : UserAction[*] nonunique;

metadata def CommandMetadata :> SemanticMetadata {
    // The meta-cast operation "userAction meta SysML::Usage" has
    // type Usage, which conforms to the type KerML::Type of baseType.
    // Since userActions is an ActionUsage, the expression evaluates
    // at model level to a value of type SysML::ActionUsage.
    :>> baseType = userActions meta SysML::Usage;
}

// Save implicitly subclassifies UserAction
// (which is the definition of userActions).
action def Save {
    @CommandMetadata;
}

// previousAction implicitly subsets userActions.
action previousAction[1] {
    @CommandMetadata;
}
