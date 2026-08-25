"""Analyst toolkit: comparable-company analysis from SEC EDGAR XBRL data.

Standard library only. No third-party dependencies are required for the core
pipeline; ``openpyxl`` is an optional extra used solely for Excel export.
"""

__version__ = "0.1.0"

__all__ = ["edgar", "normalize", "multiples", "comps", "excel_export"]
