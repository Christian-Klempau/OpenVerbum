# Locals
import backend.config as CONFIG

# Libraries
import mimetypes

mimetypes.init()


def find_file_type(file_path) -> str:
    mimestart = mimetypes.guess_type(file_path)[0]

    if mimestart is None:
        return "unknown"

    mimestart = mimestart.split("/")[0]
    return mimestart


def is_media_file(file_path) -> bool:
    file_type = find_file_type(file_path)

    if file_type not in CONFIG.ACCEPTED_FILE_TYPES:
        return False

    return True
