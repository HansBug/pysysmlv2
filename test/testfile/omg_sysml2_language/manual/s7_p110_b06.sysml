action def MonitoredActivity {
merge continue;
then action performCriticalActivity {
perform action monitorCriticalActivity;
perform action criticalActivity;
then terminate; // Terminates "performCriticalActivity" even if
// "monitorCriticalActivity" is still ongoing.
}
then decide;
if continueActivity() then continue;
else stop;
action stop terminate; // Terminates performance of "MonitoredActivity".
}
