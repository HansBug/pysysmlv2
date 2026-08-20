occurrence occ1;
occurrence occ2 {
    event occurrence evt references occ1;
    // Other than having a name, the above is equivalent to
    // event occ1;
}
