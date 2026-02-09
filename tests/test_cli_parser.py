import io
import unittest
from contextlib import redirect_stdout

from plex_music_hygiene.cli import build_parser


class TestCliParser(unittest.TestCase):
    def test_parser_exposes_expected_subcommands(self):
        parser = build_parser()
        subparser_actions = [
            a for a in parser._actions if getattr(a, "choices", None) and isinstance(a.choices, dict)
        ]
        self.assertTrue(subparser_actions, "expected subcommand action")
        commands = set(subparser_actions[0].choices.keys())
        self.assertTrue(
            {
                "export-artist-tracks",
                "retag-from-csv",
                "fix-track-numbers",
                "cleanup-artists",
                "repair-artist-posters",
                "verify-artists",
            }.issubset(commands)
        )

    def test_help_renders_without_token_requirement(self):
        parser = build_parser()
        buf = io.StringIO()
        with redirect_stdout(buf):
            parser.print_help()
        out = buf.getvalue()
        self.assertIn("Plex Music Toolkit", out)


if __name__ == "__main__":
    unittest.main()
