action def MonitoredActivity {
    first start;
    then fork;
    then performCriticalActivity;
    then waitForTimeOut;
    action performCriticalActivity {
        // monitorCriticalActivity and criticalActivity are preformed concurrently.
        perform monitorCriticalActivity;
        perform criticalActivity;
        // A terminate action ends its immediately containing action. In this case, performCriticalActivity terminates even if monitorCriticalActivity is still ongoing.
        then terminate;
    }
    then stop;
    action waitForTimeOut;
    then stop;
    // This terminates MonitoredActivity when either performCriticalActivity or waitForTimeOut completes.
    action stop terminate;
}
