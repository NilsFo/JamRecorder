"""
Util functions shared throughout this project.
"""

from datetime import datetime


def write(
        text: str
):
    """
    Formats a given input and writes it to the console.
    Removes whitespaces at the beginning and end.
    Appends the current time.

    Args:
        text: The text that should be printed in the console.

    Returns:
        None
    """
    text = str(text)
    text = text.strip()

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {text}")


def main():
    print('Nothing to see here.')


if __name__ == '__main__':
    main()
