view 'vehicle parts view' : 'Part Structure View' {
    // Recursive import is useful for exposing elements
    // from hierarchical models.
    expose VehicleDesignModel::**;

    // This is an additional filter condition.
    filter not @SysML::ConnectionUsage;

    // This implicitly redefines the view rendering from
    // the view definition.
    render asMyTreeDiagram;
}
