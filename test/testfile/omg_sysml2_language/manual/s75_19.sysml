package P4 {
    item A;
    item B;
    package Q {
        item C;
    }
}
package P5 {
    private import P4::**;
    // The above recursive import is equivalent to all
    // of the following taken together:
    //     private import P4;
    //     private import P4::*;
    //     private import P4::Q::*;
}
package P6 {
    private import P4::*::**;
    // The above recursive import is equivalent to all
    // of the following taken together:
    //     private import P4::*;
    //     private import P4::Q::*;
    // (Note that P4 itself is not imported.)
}
