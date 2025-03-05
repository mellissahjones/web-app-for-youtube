import os
import time
import threading
from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp

app = Flask(__name__, static_folder='../frontend/build', template_folder='../frontend/build')

def ensure_directory_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def delete_after_delay(filepath, delay=1800):  # 1800 seconds = 30 minutes
    time.sleep(delay)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted: {filepath}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = [{"format_id": f["format_id"], "ext": f["ext"], "resolution": f.get("resolution", "N/A")} for f in info["formats"]]
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"formats": formats})

    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download_video():
    url = request.form.get("url")
    format_id = request.form.get("format_id")

    if not url or not format_id:
        return jsonify({"error": "URL and format_id are required"}), 400

    directory = request.url_root.split('/')[-2] if '/' in request.url_root else "downloads"
    download_folder = os.path.join(directory, "downloads")
    ensure_directory_exists(download_folder)

    ydl_opts = {
        "format": format_id,
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    threading.Thread(target=delete_after_delay, args=(filename,)).start()

    return jsonify({"message": "Download complete", "filename": os.path.basename(filename)})

@app.route("/get_file/<filename>")
def get_file(filename):
    directory = request.url_root.split('/')[-2] if '/' in request.url_root else "downloads"
    download_folder = os.path.join(directory, "downloads")
    filepath = os.path.join(download_folder, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    directory = request.url_root.split('/')[-2] if '/' in request.url_root else "downloads"
    download_folder = os.path.join(directory, "downloads")
    filepath = os.path.join(download_folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": f"{filename} deleted"})
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
