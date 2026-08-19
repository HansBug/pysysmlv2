part def Processor {
    // A composite action is automatically terminated when its containing part is terminated, but a referential action is not. That is why workflowProcess was terminated explicitly in this example, but not internalProcess.
    ref action workflowProcess : WorkflowProcess;
    action internalProcess {
        // ...
    }
}
action terminateProcessing {
    in processor : Processor;
    // A terminate action can have an argument that identifies the action to be terminated (instead of the default to the containing action).
    terminate processor.workflowProcess;
    // A terminate action can also be used to terminate (“destroy”) a part.
    terminate processor;
}
