import subprocess
import http.server
import socketserver
import threading
import os

# Configuration
MIC_NAME = "Microphone (Realtek(R) Audio)"
CAMERA_NAME = "USB2.0 HD UVC WebCam"
PORT = 8000
DASH_DIRECTORY = os.path.abspath('./dash_content')
FFMPEG_CAPTURE_COMMAND = [
    'ffmpeg',
    '-f', 'dshow',
    '-i', f'video={CAMERA_NAME}:audio={MIC_NAME}',
    '-vcodec', 'libx264',
    '-acodec', 'aac',
    '-g', '30',
    '-window_size', '5000000', 
    '-segment_time', '4',  # 4-second segments
    '-f', 'dash',
    os.path.join(DASH_DIRECTORY, 'manifest.mpd')
]

# Ensure the DASH content directory exists
if not os.path.exists(DASH_DIRECTORY):
    os.makedirs(DASH_DIRECTORY)

def start_ffmpeg_capture():
    print("Starting FFmpeg capture and DASH encoding...")
    subprocess.run(FFMPEG_CAPTURE_COMMAND)



class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        http.server.SimpleHTTPRequestHandler.end_headers(self)



def start_http_server():
    os.chdir(DASH_DIRECTORY)
    # delete the existing files every time the server starts except the index.html, manifest and ends with .js
    for file in os.listdir(DASH_DIRECTORY):
        if file != 'index.html' and not file.endswith('.js') and file != 'images':
            os.remove(file)
    handler = MyHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Serving DASH content and HTML page at http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    # Start FFmpeg capture and DASH encoding in a separate thread
    threading.Thread(target=start_ffmpeg_capture, daemon=True).start()

    # Start the HTTP server in the main thread
    start_http_server()
