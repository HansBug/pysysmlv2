package Viewpoints {
    part def SafetyEngineer;
    concern def VehicleSafety {
        doc /* Vehicle must have necessary safety features. */
        stakeholder se : SafetyEngineer;
    }
    viewpoint safetyViewpoint {
        frame concern vs : VehicleSafety;
    }
}
package ViewDefinitions {
    view def TreeView {
        render asTreeDiagram;
    }
    view def PartsTreeView :> TreeView {
        filter @SysML::PartUsage;
    }
}
