requirement r1 : R1 subsets Requirements::requirementChecks {
    subject subj redefines R1::subj;
    assume constraint ca subsets Requirements::RequirementCheck::assumptions;
    require constraint cr subsets Requirements::RequirementCheck::constraints;
}
