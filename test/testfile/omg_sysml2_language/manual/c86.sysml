action def TakePicture {
  // The following two features are considered parameters.
  in scene : Scene;
  out picture : Picture;

  bind focus.scene = scene;
  action focus : Focus { in scene; out image; }
  first focus then shoot;
  flow focus.image to shoot.image;
  action shoot : Shoot { in image; out picture; }
  bind picture = focus.picture;
}
