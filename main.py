from backend.utils import is_media_file, find_file_type
from backend.config import ACCEPTED_FILE_TYPES
from backend.metadata import MetaData

from frontend.ui import create_ui, launch_ui


class Backend:
    def __init__(self) -> None:
        pass

    def validate_file(self, file_path: str) -> bool:
        if not is_media_file(file_path):
            return False

        return True

    def process_file(self, file_path) -> None:
        file_type = find_file_type(file_path)

        if not self.validate_file(file_path):
            SIGNALS.process_error.emit(
                f"File not supported (use {', '.join(ACCEPTED_FILE_TYPES)} files)"
            )
            return

        md = MetaData(SIGNALS, file_path, file_type)
        md.start()


if __name__ == "__main__":
    backend = Backend()
    app, window = create_ui()
    SIGNALS = window.signals

    # front calling back
    SIGNALS.process_requested.connect(backend.process_file)

    # back calling front
    SIGNALS.process_error.connect(window.handle_error)
    SIGNALS.process_info.connect(window.handle_info)
    SIGNALS.advance_bar.connect(window.advance_bar)

    launch_ui(app, window)
