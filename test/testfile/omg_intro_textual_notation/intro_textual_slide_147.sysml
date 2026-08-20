standard library package RiskMetadata {
    private import ScalarValues::Real;
    attribute def Level :> Real {
        assert constraint { that >= 0.0 and that <= 1.0 }
    }
    enum def LevelEnum :> Level {
        low = 0.25;
        medium = 0.50;
        high = 0.75;
    }
    // General risk level in terms of probability and impact.
    attribute def RiskLevel {
        attribute probability : Level;
        attribute impact : Level [0..1];
    }
    // Standard low, medium and high risk levels.
    enum def RiskLevelEnum :> RiskLevel {
        low = RiskLevel(probability = LevelEnum::L);
        medium = RiskLevel(probability = LevelEnum::M);
        high = RiskLevel(probability = LevelEnum::H);
    }
    // To be used to annotate model elements as to their risk level in typical risk areas.
    metadata def Risk {
        attribute totalRisk : RiskLevel [0..1];
        attribute technicalRisk : RiskLevel [0..1];
        attribute scheduleRisk : RiskLevel [0..1];
        attribute costRisk : RiskLevel [0..1];
    }
}
