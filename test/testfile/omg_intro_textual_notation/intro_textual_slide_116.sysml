// A viewpoint is a requirement to present information from a model in a view that addresses certain stakeholder concerns.
// Any requirement may be modeled as framing relevant stakeholder concerns, not just viewpoints.
viewpoint 'system structure perspective' {
    // A viewpoint frames the concerns that will be addressed by a view that satisfies the viewpoint.
    frame 'system breakdown';
    frame modularity;
    require constraint {
        doc /*
        * A system structure view shall show the hierarchical
        * part decomposition of a system, starting with a
        * specified root part.
        */
    }
}
