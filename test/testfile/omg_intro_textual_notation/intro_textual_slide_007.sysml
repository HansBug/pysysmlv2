package 'Comment Example' {
    /* This is comment, part of the model,
    * annotating (by default) it's owning package. */
    // A comment begins with /* and ends with */.
    // A comment can optionally be named.
    comment Comment1 /* This is a named comment. */
    // What the comment annotates can be explicitly specified (it is the owning namespace by default).
    comment about Automobile
    /* This is an unnamed comment, annotating an
    * explicitly specified element.
    */
    part def Automobile;
    // Import and alias declarations can also be commented.
    alias Car for Automobile {
        /* This is a comment annotating its owning
        * element.
        */
    }

    // This is a note. It is in the text, but not part
    // of the model.
    // A note begins with // and extends to the end of the line. (A multiline note begins with //* and ends with */.)
    alias Torque for ISQ::TorqueValue;
}
