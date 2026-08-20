part def Camera {
  action focus[*] : Focus;
  action shoot[*] : Shoot;
  // Each focus may be preceded by a previous focus.
  succession multiFocusing
    first [0..1] focus then [0..1] focus;
  // Each shoot must follow a focus.
  first [1] focus then [0..1] shoot;
  // The Camera can be focused after shooting.
  first [0..1] shoot then focus;
}
