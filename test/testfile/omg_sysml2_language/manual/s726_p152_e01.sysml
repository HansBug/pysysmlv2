view def 'Part Structure View' {
    import Views::*;

    filter @SysML::PartUsage;
    render asTreeDiagram;
}
