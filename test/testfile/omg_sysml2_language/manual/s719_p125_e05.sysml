calc def Average {
    in scores[1..*] : Rational;
    return : Rational = sum(scores) / size(scores);
}
