from config.settings import MIN_TEXT_LENGTH

def is_image_based_resume(text: str) -> bool:
    return len(text) < MIN_TEXT_LENGTH
