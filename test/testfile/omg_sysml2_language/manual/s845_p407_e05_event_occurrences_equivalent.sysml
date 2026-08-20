occurrence occ1 subsets Occurrences::occurrences;
occurrence occ2 subsets Occurrences::occurrences {
    ref occurrence evt references occ1
        subsets Occurrences::Occurrence::timeEnclosedOccurrences;
}
