standard library package ModelingMetadata {
    ...
    // To be used to annotate model elements with status information.
    enum def StatusKind {
        open;
        tbd; // To be determined
        tbr; // To be resolved
        tbc; // To be confirmed
        done;
        closed;
    }
    metadata def StatusInfo {
        attribute originator : String [0..1];
        attribute owner : String [0..1];
        attribute status : StatusKind;
        attribute risk : Risk [0..1];
    }
    // To be used to give rationale for a model element.
    metadata def Rationale {
        attribute text : String;
        // This is an optional reference to a feature that further explains this rationale (e.g., a trade study analysis).
        ref explanation : Anything [0..1];
    }
    // Generic issue annotation.
    metadata def Issue {
        attribute text : String;
    }
    // To be used to model a dependency in which source elements refine target elements.
    metadata def <refinement> Refinement {
        :>> annotatedElement : SysML::Dependency;
    }
}
