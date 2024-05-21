鍵盤快速鍵更新 … 
Google 雲端硬碟將在 2024年8月1日 星期四更新鍵盤快速鍵，讓你透過首字母導覽功能找到所需項目。瞭解詳情

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import signal
import datetime

split_time = 600000000000

# Function to create the pipeline string
def create_pipeline():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    eo_location = "rtsp://admin:53373957@192.168.144.108:554/cam/realmonitor?channel=1&subtype=2"
    ir_location = "rtsp://admin:53373957@192.168.144.6:8554/avix"

    pipeline_str = (
        f"rtspsrc location={eo_location} ! "
        "rtph264depay ! "
        "h264parse ! "
        f"splitmuxsink location={now}_eo_video_%d.mkv async-finalize=false max-size-time={split_time} "
        "muxer=matroskamux muxer-properties=\"properties,streamable=true\" "
        f"rtspsrc location={ir_location} ! "
        "rtph264depay ! "
        "h264parse ! "
        f"splitmuxsink location={now}_ir_video_%d.mkv async-finalize=false max-size-time={split_time} "
        "muxer=matroskamux muxer-properties=\"properties,streamable=true\""
    )


    return pipeline_str
if __name__ == "__main__":
    # Create the GStreamer pipeline
    print(create_pipeline())

    # Initialize GStreamer
    Gst.init(None)
    pipeline = Gst.parse_launch(create_pipeline())

    # Function to handle messages from the pipeline
    def on_message(bus, message, loop):
        mtype = message.type
        if mtype == Gst.MessageType.EOS:
            print("End of stream")
            loop.quit()
        elif mtype == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, {debug}")
            loop.quit()

    # Function to gracefully handle termination
    def signal_handler(sig, frame):
        print('Interrupt received, stopping...')
        pipeline.send_event(Gst.Event.new_eos())

    # Connect to the pipeline's bus to receive messages
    bus = pipeline.get_bus()
    bus.add_signal_watch()

    # Create a GLib MainLoop
    loop = GLib.MainLoop()

    # Add signal handler for SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    # Add a message handler to the bus
    bus.connect("message", on_message, loop)

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # Clean up
    pipeline.set_state(Gst.State.NULL)

