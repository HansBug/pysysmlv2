// A view definition specifies how information can be extracted from a model in order to satisfy one or more viewpoints.
view def 'Part Structure View' {
    satisfy 'system structure perspective';
    filter @SysML::PartUsage;
}
view 'vehicle structure view' :
'Part Structure View' {
    // A view usage exposes the model elements to be included in the view, which are filtered as specified in the view definition.
    expose vehicle::**;
    // A view usage specifies how the view is to be rendered as a physical artifact.
    render asTreeDiagram;
}
