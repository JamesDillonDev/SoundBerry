import subprocess

current_process = None
volume = 100


def play_stream(stream):
    global current_process

    current_process = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-volume", str(volume), "-"],
        stdin=subprocess.PIPE
    )

    try:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            current_process.stdin.write(chunk)
    except Exception:
        pass

    current_process.stdin.close()
    current_process.wait()
    current_process = None


def play_file(path):
    global current_process

    current_process = subprocess.Popen(
        ["ffplay", "-nodisp", "-autoexit", "-volume", str(volume), path]
    )


def stop_audio():
    global current_process

    if current_process:
        current_process.kill()
        current_process = None


def set_volume(v):
    global volume
    volume = int(v)


def get_status():
    return {
        "state": "playing" if current_process else "idle",
        "volume": volume
    }