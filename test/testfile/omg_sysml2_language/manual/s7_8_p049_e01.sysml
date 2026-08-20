enum def ConditionColor { red; green; yellow; }
attribute def ConditionLevel {
    attribute color : ConditionColor;
}
enum def RiskLevel :> ConditionLevel {
    enum low { :>> color = ConditionColor::green; }
    enum medium { :>> color = ConditionColor::yellow; }
    enum high { :>> color = ConditionColor::red; }
}
