view 'vehicle parts view' : 'Part Structure View' {
    // This applies the filter directly to the imported
    // elements from the expose relationships. (The filter
    // conditions from the view definition also still apply.)
    expose VehicleDesignModel::**[not @SysML::ConnectionUsage];

    render asMyTreeDiagram;
}
