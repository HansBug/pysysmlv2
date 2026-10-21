targetTransitionUsage
    : emptyParameterMember ( TRANSITION ( emptyParameterMember triggerActionMember )? ( guardExpressionMember )? ( effectBehaviorMember )? | emptyParameterMember triggerActionMember ( guardExpressionMember )? ( effectBehaviorMember )? | guardExpressionMember ( effectBehaviorMember )? )? THEN transitionSuccessionMember actionBody
    ;
