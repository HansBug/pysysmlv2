attribute monthsInYear : Natural = 12;
item def TestRecord {
  attribute scores[1..*] : Integer;
  derived attribute averageScore[1] : Rational = sum(scores)/size(scores);
  attribute cutoff : Integer default = 0.75 * averageScore;
}
