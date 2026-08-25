"""Command line interface.

    python -m analyst_toolkit.cli comps --offline
    python -m analyst_toolkit.cli comps --peers C,JPM,BAC --bank --out comps.csv
    python -m analyst_toolkit.cli regress --offline
"""

import argparse
import os
import sys
from typing import List, Optional

from . import comps as comps_mod
from . import csv_input, excel_export, multiples
from .csv_input import CsvInputError
from .edgar import EdgarClient, EdgarError, OfflineClient

DEFAULT_BANK_PEERS = "C,JPM,BAC,WFC,GS,MS"
DEFAULT_FISCAL_YEAR = 2024


def _make_client(args):
    fixture_dir = args.fixture_dir or comps_mod.default_fixture_dir()
    if args.offline:
        return OfflineClient(fixture_dir)
    return EdgarClient(cache_dir=args.cache_dir)


def _resolve_prices(args) -> dict:
    if args.prices:
        return comps_mod.load_prices(args.prices)
    default_path = os.path.join(
        args.fixture_dir or comps_mod.default_fixture_dir(), "prices_sample.json"
    )
    if os.path.isfile(default_path):
        return comps_mod.load_prices(default_path)
    return {}


def _resolve_template(args) -> str:
    """Determine the column template, with --bank kept as a shorthand alias."""
    if getattr(args, "template", None):
        return args.template
    if getattr(args, "bank", False):
        return "bank"
    return "industrial"


def _load_comps(args):
    """Load a comps result from whichever source the arguments specify.

    Returns ``(result, source_note)``. Shared by both subcommands so the CSV
    path is available everywhere, not just for the comps table.
    """
    if args.input_csv:
        # Manual path for issuers not on EDGAR (Indian listed companies).
        records = csv_input.load_financials_csv(args.input_csv, args.fiscal_year)
        prices = csv_input.prices_from_records(records)
        if args.prices:
            prices.update(comps_mod.load_prices(args.prices))
        result = comps_mod.build_comps_from_records(records, args.fiscal_year, prices)
        return result, "manual CSV: {0}".format(args.input_csv)

    tickers: List[str] = [t for t in args.peers.split(",") if t.strip()]
    client = _make_client(args)
    prices = _resolve_prices(args)
    result = comps_mod.build_comps(client, tickers, args.fiscal_year, prices)
    return result, ("fixtures" if args.offline else "SEC EDGAR")


def cmd_comps(args) -> int:
    template = _resolve_template(args)
    result, source_note = _load_comps(args)

    if not result["rows"]:
        sys.stderr.write("No data retrieved for any ticker.\n")
        for line in comps_mod.coverage_report(result):
            sys.stderr.write("  {0}\n".format(line))
        return 1

    columns = comps_mod.COLUMN_TEMPLATES[template]
    table = comps_mod.to_table(result, columns)

    print(
        "\nComparable companies — FY{0}  ({1} template, source: {2})".format(
            result.get("fiscal_year") or args.fiscal_year, template, source_note
        )
    )
    print(excel_export.render_text(table))

    if args.out:
        path = excel_export.write(table, args.out, fmt=args.format, raw=args.raw)
        print("\nWritten to {0}".format(path))

    # Suppress fields that don't apply to the issuer type being analysed.
    if template == "bank":
        ignore = comps_mod.INDUSTRIAL_ONLY_FIELDS
    elif template in ("amc", "depository"):
        ignore = comps_mod.FEE_BUSINESS_IGNORE_FIELDS
    else:
        ignore = comps_mod.BANK_ONLY_FIELDS
    report = comps_mod.coverage_report(result, ignore=ignore)
    if report:
        print("\nData coverage notes:")
        for line in report:
            print("  {0}".format(line))
    else:
        print("\nAll expected fields resolved for every ticker.")

    return 0


def cmd_regress(args) -> int:
    """Regress P/TBV on ROTE across a peer set.

    The empirical backbone of bank relative valuation — see
    docs/bank-valuation-primer.md. Also works on any peer set where returns on
    book are the relevant driver, including capital-light financials loaded from
    a manual CSV.
    """
    result, _ = _load_comps(args)
    observations = [
        (row["ticker"], row.get("rote"), row.get("p_tbv"))
        for row in result["rows"]
        if row.get("rote") is not None and row.get("p_tbv") is not None
    ]

    if len(observations) < 2:
        sys.stderr.write(
            "Need at least two peers with both ROTE and P/TBV to regress; "
            "got {0}.\n".format(len(observations))
        )
        return 1

    xs = [obs[1] for obs in observations]
    ys = [obs[2] for obs in observations]
    slope, intercept, r_squared = multiples.linear_regression(xs, ys)

    print("\nP/TBV vs. ROTE regression — FY{0}".format(args.fiscal_year))
    print(
        "  P/TBV = {0:.3f} x ROTE {1} {2:.3f}".format(
            slope, "+" if intercept >= 0 else "-", abs(intercept)
        )
    )
    print("  R-squared = {0:.3f}   (n = {1})".format(r_squared, len(observations)))

    print("\n  {0:<8} {1:>8} {2:>8} {3:>9} {4:>10}".format(
        "Ticker", "ROTE", "P/TBV", "Fitted", "Residual"
    ))
    print("  " + "-" * 47)
    for ticker, rote, ptbv in sorted(observations, key=lambda o: o[1], reverse=True):
        fitted = slope * rote + intercept
        residual = ptbv - fitted
        print(
            "  {0:<8} {1:>7.1f}% {2:>7.2f}x {3:>8.2f}x {4:>+9.2f}".format(
                ticker, rote * 100, ptbv, fitted, residual
            )
        )

    print(
        "\n  Interpretation: a negative residual means the company trades below\n"
        "  the level its returns imply. Decide whether that is an unexplained\n"
        "  discount or the market doubting the reported returns."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyst_toolkit",
        description="Comparable company analysis from SEC EDGAR XBRL data.",
    )
    subparsers = parser.add_subparsers(dest="command")

    def add_common(sub):
        sub.add_argument(
            "--peers",
            default=DEFAULT_BANK_PEERS,
            help="Comma-separated tickers (default: %(default)s)",
        )
        sub.add_argument(
            "--fiscal-year",
            type=int,
            default=DEFAULT_FISCAL_YEAR,
            dest="fiscal_year",
            help="Fiscal year to pull (default: %(default)s)",
        )
        sub.add_argument(
            "--offline",
            action="store_true",
            help="Run from bundled fixtures instead of calling EDGAR",
        )
        sub.add_argument(
            "--fixture-dir",
            dest="fixture_dir",
            default=None,
            help="Override the offline fixture directory",
        )
        sub.add_argument(
            "--cache-dir",
            dest="cache_dir",
            default=None,
            help="Cache EDGAR responses here to avoid repeat requests",
        )
        sub.add_argument(
            "--prices",
            default=None,
            help="JSON file of share prices and share counts",
        )
        sub.add_argument(
            "--input-csv",
            dest="input_csv",
            default=None,
            help=(
                "Load financials from a manual CSV instead of EDGAR. Required "
                "for non-SEC filers such as Indian listed companies."
            ),
        )

    comps_parser = subparsers.add_parser("comps", help="Build a comps table")
    add_common(comps_parser)
    comps_parser.add_argument(
        "--template",
        choices=sorted(comps_mod.COLUMN_TEMPLATES),
        default=None,
        help=(
            "Column template. 'bank' uses P/TBV and ROTE with no EV multiples; "
            "'amc' uses P/AUM and blended yield; 'depository' uses per-account "
            "metrics. Default: industrial."
        ),
    )
    comps_parser.add_argument(
        "--bank",
        action="store_true",
        help="Shorthand for --template bank",
    )
    comps_parser.add_argument("--out", default=None, help="Output file path")
    comps_parser.add_argument(
        "--format", choices=["csv", "xlsx"], default=None, help="Output format"
    )
    comps_parser.add_argument(
        "--raw",
        action="store_true",
        help="Write unformatted numbers rather than display strings",
    )
    comps_parser.set_defaults(func=cmd_comps)

    regress_parser = subparsers.add_parser(
        "regress", help="Regress P/TBV on ROTE across a bank peer set"
    )
    add_common(regress_parser)
    regress_parser.set_defaults(func=cmd_regress)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except CsvInputError as exc:
        sys.stderr.write("\nCSV input error: {0}\n".format(exc))
        return 2
    except EdgarError as exc:
        sys.stderr.write("\nEDGAR error: {0}\n".format(exc))
        return 2
    except RuntimeError as exc:
        sys.stderr.write("\nError: {0}\n".format(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
