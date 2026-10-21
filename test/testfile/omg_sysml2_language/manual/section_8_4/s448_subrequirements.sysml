requirement def Rqt specializes Requirements::RequirementCheck {
    requirement rqt1 subsets Requirements::RequirementCheck::subrequirements;
    ref requirement rqt2 subsets Requirements::requirements,
        Performances::enclosedPerformances;
}
