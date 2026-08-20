// The above is equivalent to the following.
occurrence def Flight {
  timeslice preflight[1];
  first preflight then inflight;
  timeslice inflight[1];
  first inflight then postflight;
  timeslice postflight[1];
}
