#!/usr/bin/env python3

"""
Application main class. Shows text user interface for interactive dictionary.
"""

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Header, Label, Input, RichLog
from rich.text import Text

from sset import SSet

FILENAME = "words.txt"

# Messages for footer
LOADING = Text.from_markup("Loading dictionary...")
SHOW_LIMIT = 1000


def footer_markup(cnt: int) -> Text:
    """Returns markup for footer text."""
    if cnt == 0:
        return Text.from_markup("Press [yellow]Ctrl-C[/] to exit.")
    if cnt <= SHOW_LIMIT:
        return Text.from_markup(f"Press [yellow]Ctrl-C[/] to exit. [blue]{cnt}[/] results.")
    return Text.from_markup(f"Press [yellow]Ctrl-C[/] to exit. [blue]{cnt}[/] results. [bold]Type one more letter...")


class SearcherApp(App):
    """A textual app to interactively search in dictionary"""

    TITLE = "Interactive Dictionary Search"
    SUB_TITLE = "It's free (and we don't spy on you, honestly!)"

    sset = SSet(FILENAME)

    def compose(self) -> ComposeResult:
        """Returns application window"""
        yield Header(show_clock=True)
        yield Input(placeholder="Type a string, e.g. squire")
        yield RichLog(id="results")
        yield Label(LOADING)

    async def on_mount(self) -> None:
        """Called when app starts"""
        # Give the input focus, so we can start typing
        self.query_one(Input).focus()
        self.query_one("#results", RichLog).loading = True

    async def on_ready(self) -> None:
        """Called when app is ready"""
        self.sset.load()
        self.query_one("#results", RichLog).loading = False
        self.query_one(Label).update(footer_markup(0))

    async def on_input_changed(self, message: Input.Changed) -> None:
        """Handles a changed text message."""
        log = self.query_one("#results", RichLog)
        if len(message.value) > 0:
            self.query_one(Label).update(footer_markup(0))
            log.loading = True
            self.lookup_word(message.value)
        else:
            # Clear results
            self.query_one(Label).update(footer_markup(0))
            log.loading = False
            log.clear()

    @work(exclusive=True)
    async def lookup_word(self, substr: str) -> None:
        """Writes a list of words into results."""
        results = self.sset.search(substr)
        cnt = len(results)
        if cnt <= SHOW_LIMIT:
            log = self.query_one("#results", RichLog)
            log.clear()
            for w in results:
                pos = w.find(substr)
                if pos == -1:
                    # wrong, no substr in word
                    log.write(Text.from_markup(f"[strike bold red]{w}"))
                else:
                    n = len(substr)
                    before = w[0:pos]
                    word = w[pos:pos+n]
                    after = w[pos+n:]
                    markup = before + "[bold green]" + word + "[/]" + after
                    log.write(Text.from_markup(markup))
            log.loading = False
        self.query_one(Label).update(footer_markup(cnt))


if __name__ == "__main__":
    app = SearcherApp()
    app.run()
