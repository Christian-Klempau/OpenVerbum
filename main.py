from backend.voice_wrapper import VoiceProcessor

from frontend.ui import create_ui, launch_ui

import global_config as G_CONFIG

if __name__ == "__main__":
    app, window = create_ui(G_CONFIG)
    SIGNALS = window.signals
    backend = VoiceProcessor(SIGNALS)

    # front calling back
    SIGNALS.process_requested.connect(backend.process_file)

    # back calling front
    SIGNALS.process_error.connect(window.handle_error)
    SIGNALS.process_info.connect(window.handle_info)
    SIGNALS.process_started.connect(window.start_process)
    SIGNALS.process_done.connect(window.finish_process)

    SIGNALS.advance_bar.connect(window.advance_bar)

    launch_ui(app, window)
