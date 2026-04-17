from datetime import datetime


def write(text: str):
    text = str(text)
    text = text.strip()

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {text}")


def main():
    print('Nothing to see here.')


if __name__ == '__main__':
    main()
