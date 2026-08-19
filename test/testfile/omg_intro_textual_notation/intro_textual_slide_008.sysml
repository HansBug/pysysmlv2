package 'Documentation Example' {
    doc  /* This is documentation of the owning
    * package.
    */
    // Documentation is a special kind of comment that is directly owned by the element it documents.
    part def Automobile {
        // A documentation comment can be optionally named like a regular comment.
        doc Document1
        /* This is documentation of Automobile. */
    }
    alias Car for Automobile {
        doc /* This is documentation of the alias. */
    }
    alias Torque for ISQ::TorqueValue;
}
