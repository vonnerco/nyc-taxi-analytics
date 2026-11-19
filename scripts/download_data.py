"""Download the pinned TLC quarter and zone lookup into data/raw/.

Yellow taxi, Q1 2024 (January-March): roughly 145 MB of parquet, gitignored,
so this is the one network step. Existing files are skipped.
Run from anywhere: python scripts/download_data.py
"""

from pathlib import Path
import urllib.request

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BASE = "https://d37ci6vzurychx.cloudfront.net"
MONTHS = ("01", "02", "03")


def fetch(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"exists  {dest.relative_to(ROOT)}")
        return
    print(f"fetch   {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for month in MONTHS:
        name = f"yellow_tripdata_2024-{month}.parquet"
        fetch(f"{BASE}/trip-data/{name}", RAW / name)
    csv_path = RAW / "taxi_zone_lookup.csv"
    fetch(f"{BASE}/misc/taxi_zone_lookup.csv", csv_path)
    # The TLC CSV ships with a UTF-8 BOM; strip it so LocationID reads cleanly.
    csv_path.write_text(csv_path.read_text(encoding="utf-8-sig"), encoding="utf-8")

    # dbt reads parquet only, so convert the lookup once here.
    zone_parquet = RAW / "taxi_zone_lookup.parquet"
    with duckdb.connect() as con:
        con.execute(
            "copy (select * from read_csv_auto('{src}')) to '{dst}' (format parquet)".format(
                src=csv_path.as_posix(), dst=zone_parquet.as_posix()
            )
        )
    print(f"wrote   {zone_parquet.relative_to(ROOT)}")
    print("done - next: cd dbt_project; dbt build --profiles-dir .")


if __name__ == "__main__":
    main()
