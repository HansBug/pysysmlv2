// A view definition specifies how information can be extracted from a model in order to satisfy one or more viewpoints.
// A view definition can filter the elements to be included in the views it specifies.
// The SysML library package models the SysML abstract syntax, which can be used to filter on specific kinds of model elements.
// The view rendering can also be given in the view definition, in which case it will be the same for all usages of that definition. But only view usages can expose elements to be viewed.
view def 'Part Structure View' {
    satisfy 'system structure perspective';
    filter @SysML::PartUsage;
}
// A view usage specifies a certain view conforming to a view definition.
view 'vehicle structure view' :
'Part Structure View' {
    // A view usage exposes the model elements to be included in the view, which are filtered as specified in the view definition.
    expose vehicle::**;
    // A view usage specifies how the view is to be rendered as a physical artifact.
    render asTreeDiagram;
}
