part processor {
private ref action process : ProcessWorkflow;
action startProcessing {
assign process := new ProcessWorkFlow();
}
action terminateProcessing {
// The following terminate action has the name "terminate1".
action terminate1 terminate process; // Terminates "process" action.
// The following terminate action is unnamed.
terminate this; // Terminates "processor" part.
}
}
