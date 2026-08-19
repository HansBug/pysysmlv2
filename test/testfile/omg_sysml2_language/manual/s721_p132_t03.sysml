part part1 {
    satisfy requirement11
    by part1 {
        bind 'requirement11-1'.x1 = a;
        bind 'requirement11-2'.x2 = b;
    }
}
