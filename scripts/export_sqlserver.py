"""Generate synthetic INSERT batches; no SQL Server credentials required."""
import argparse
from pathlib import Path
from src.local_engine import read_tables

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="artifacts/load_synthetic.sql")
args = parser.parse_args()
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w") as handle:
    handle.write("-- Only synthetic data. Run in the disposable workshop database.\nSET NOCOUNT ON;\n")
    for name, rows in read_tables().items():
        columns = list(rows[0])
        for offset in range(0, len(rows), 500):
            values = []
            for row in rows[offset:offset + 500]:
                values.append("(" + ",".join("'" + row[key].replace("'", "''") + "'" for key in columns) + ")")
            handle.write(f"INSERT INTO dbo.{name} ({','.join(columns)}) VALUES\n" + ",\n".join(values) + ";\nGO\n")
print(out)
