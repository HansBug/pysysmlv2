requirement def R2 specializes Requirements::RequirementCheck {
    subject subj redefines Requirements::RequirementCheck::subj;
    assume constraint ca subsets Requirements::RequirementCheck::assumptions;
    require constraint cr subsets Requirements::RequirementCheck::constraints;
}
