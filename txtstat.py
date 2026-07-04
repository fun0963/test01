import sys


def compute_stats(text):
    lines = len(text.splitlines())
    words = len(text.split())
    chars = len(text)
    return lines, words, chars


def main():
    if len(sys.argv) < 2:
        print("error: missing filename argument", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    lines, words, chars = compute_stats(text)
    print(f"lines={lines} words={words} chars={chars}")


if __name__ == "__main__":
    main()
