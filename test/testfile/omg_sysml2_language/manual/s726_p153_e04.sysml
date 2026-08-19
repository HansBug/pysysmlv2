concern 'system breakdown' {
    stakeholder se : 'Systems Engineer';
    stakeholder ivv : 'IV&V';
}
concern 'modularity' {
    stakeholder se : 'Systems Engineer';
}

viewpoint def 'System Structure Perspective' {
    frame 'system breakdown';
    frame 'modularity';

    require constraint {
        doc
        /* A system structure view shall show the hierarchical
         * part decomposition of a system, starting with a
         * specified root part.
         */
    }
}
