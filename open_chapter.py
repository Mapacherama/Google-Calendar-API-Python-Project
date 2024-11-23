import webbrowser
import sys

def open_chapter(chapter_url):
    webbrowser.open(chapter_url)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python open_chapter.py <chapter_url>")
        sys.exit(1)

    chapter_url = sys.argv[1]
    open_chapter(chapter_url)