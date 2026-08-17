import logging
import pytest

from xcpngutils import configure_logging

class TestFormatter:
    def test_newline_msg(self, capsys):
        logger = configure_logging("test")
        logger.error("This is a\n newline.")

        captured = capsys.readouterr()
        assert "This is a\n newline." not in captured.out
        assert "This is a\\n newline." in captured.out

    def test_newline_arg(self, capsys):
        logger = configure_logging("test")
        logger.error("This is a newline: %s.", "\n")

        captured = capsys.readouterr()
        assert "This is a newline: \n." not in captured.out
        assert "This is a newline: \\n." in captured.out
