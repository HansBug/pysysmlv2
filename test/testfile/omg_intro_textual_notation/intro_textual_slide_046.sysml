part camera : Camera {
    port viewPort;
    port displayPort;
    action takePicture : TakePicture {
        // An accept action can be via a specific port, meaning that the transfer is expected to be received by that port.
        action trigger accept scene : Scene via viewPort;
        then action focus : Focus {
            in scene = trigger.scene;
            out image;
        }
        flow from focus.image to shoot.image;
        then action shoot : Shoot {
            in image;
            out picture;
        }
        // An asynchronous transfer sent via a port has that port as its source. The target of the transfer is determined by what the port is connected to.
        // A send action can also be sent via a port, meaning that the transfer is sent out from that port.
        then send new Show(shoot.picture) via displayPort;
    }
}
