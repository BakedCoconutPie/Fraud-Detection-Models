"""Compatibility entry point for external Mamba evaluation.

PasteTrace is the only external test dataset, prepared under
``data/mamba/test_sequences``. This file delegates to the current test command.
"""

from argparse import Namespace

from src.models.mamba_model import cmd_test


if __name__ == "__main__":
    cmd_test(Namespace())
