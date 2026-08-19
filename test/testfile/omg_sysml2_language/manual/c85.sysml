item def Scene;
part camera {
  port viewPort;
  port displayPort;
  perform action takePicture {
    action trigger accept scene : Scene {
      in :>> receiver = viewPort;
    }
    then action focus {
      in item scene = trigger.scene;
      out item image;
    }
    succession flow from focus.image to shoot.image;
    action shoot {
      in item image;
      out item picture;
    }
    then action sendPicture send {
      in picture :>> payload = shoot.picture;
      in :>> sender = camera.displayPort;
    }
  }
}
part screen {
  port displayPort;
}
