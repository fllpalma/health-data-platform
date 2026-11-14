"""Generate a SYNTHETIC Apple Health export (zip) for CI and demos. No real data, ever.

It deliberately reproduces the traps found in real exports, so tests prove the fixes keep working:
- iPhone + Watch counting the same steps (overlap)          -> ADR 0004
- exact duplicate records                                    -> ADR 0004
- overlapping "in bed" records from one sleep app            -> ADR 0005
- a 20-hour "in bed" glitch                                  -> ADR 0005
- two Watches reporting the same stand hours                 -> ADR 0005

Run it:
    uv run python -m health_platform.synthetic data/synthetic/synthetic_export.zip

(Never put it in data/inbox/: the Airflow DAG watches that folder for REAL exports.)
"""

import argparse
import random
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import quoteattr

FIRST_DAY = date(2026, 10, 1)
DAYS = 21
GLITCH_NIGHT = 10  # day index with a 20-hour in-bed record
PHONE, WATCH, WATCH_2, SLEEP_APP = (
    "Synthetic iPhone",
    "Synthetic Watch",
    "Synthetic Watch 2",
    "Synthetic Sleep App",
)


def _ts(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M:%S +0000")


def _record(
    kind: str, source: str, start: datetime, end: datetime, value, unit: str | None = None
) -> str:
    prefix = (
        "HKCategoryTypeIdentifier"
        if kind in {"SleepAnalysis", "AppleStandHour"}
        else "HKQuantityTypeIdentifier"
    )
    attrs = {
        "type": prefix + kind,
        "sourceName": source,
        "sourceVersion": "1.0",
        "unit": unit,
        "creationDate": _ts(end),
        "startDate": _ts(start),
        "endDate": _ts(end),
        "value": str(value),
    }
    return (
        " <Record "
        + " ".join(f"{k}={quoteattr(v)}" for k, v in attrs.items() if v is not None)
        + "/>"
    )


def build_records(seed: int = 42) -> list[str]:
    rng = random.Random(seed)  # fixed seed -> identical file on every run (deterministic)
    rows: list[str] = []
    for i in range(DAYS):
        day = datetime.combine(FIRST_DAY + timedelta(days=i), datetime.min.time())

        for hour in range(8, 21):
            start = day + timedelta(hours=hour, minutes=5)
            end = start + timedelta(minutes=40)
            phone_steps = rng.randint(200, 900)
            if hour % 4 == 0:  # phone left on the desk: only the Watch counts
                rows.append(_record("StepCount", WATCH, start, end, phone_steps + 300, "count"))
            else:  # walking with both: they count the SAME steps (overlap)
                rows.append(_record("StepCount", PHONE, start, end, phone_steps, "count"))
                rows.append(
                    _record("StepCount", WATCH, start, end, int(phone_steps * 0.97), "count")
                )
            rows.append(
                _record(
                    "DistanceWalkingRunning",
                    PHONE,
                    start,
                    end,
                    round(phone_steps * 0.0007, 3),
                    "km",
                )
            )
            rows.append(
                _record("ActiveEnergyBurned", WATCH, start, end, rng.randint(10, 60), "kcal")
            )
            rows.append(
                _record("HeartRate", WATCH, start, start, rng.randint(60, 110), "count/min")
            )
            stood = day + timedelta(hours=hour)
            rows.append(
                _record(
                    "AppleStandHour",
                    WATCH,
                    stood,
                    stood + timedelta(hours=1),
                    "HKCategoryValueAppleStandHourStood",
                )
            )
            if hour in (
                9,
                10,
            ):  # an old second Watch reports the same hours (duplicate stand hours)
                rows.append(
                    _record(
                        "AppleStandHour",
                        WATCH_2,
                        stood,
                        stood + timedelta(hours=1),
                        "HKCategoryValueAppleStandHourStood",
                    )
                )

        workout = day + timedelta(hours=18)
        rows.append(
            _record(
                "AppleExerciseTime",
                WATCH,
                workout,
                workout + timedelta(minutes=30),
                rng.randint(15, 45),
                "min",
            )
        )
        rows.append(
            _record(
                "FlightsClimbed",
                PHONE,
                workout,
                workout + timedelta(minutes=5),
                rng.randint(1, 12),
                "count",
            )
        )
        rows.append(
            _record(
                "RestingHeartRate",
                WATCH,
                day,
                day + timedelta(hours=23),
                rng.randint(50, 65),
                "count/min",
            )
        )
        rows.append(
            _record(
                "HeartRateVariabilitySDNN",
                WATCH,
                day + timedelta(hours=3),
                day + timedelta(hours=3),
                rng.randint(30, 80),
                "ms",
            )
        )
        rows.append(
            _record(
                "WalkingHeartRateAverage",
                WATCH,
                day,
                day + timedelta(hours=23),
                rng.randint(90, 110),
                "count/min",
            )
        )

        # Sleep for the night ending on this day's morning
        bed = day - timedelta(hours=1)  # 23:00 the evening before
        rows.append(
            _record(
                "SleepAnalysis",
                PHONE,
                bed,
                bed + timedelta(hours=7, minutes=50),
                "HKCategoryValueSleepAnalysisInBed",
            )
        )
        rows.append(
            _record(
                "SleepAnalysis",
                SLEEP_APP,
                bed,
                bed + timedelta(hours=8),
                "HKCategoryValueSleepAnalysisInBed",
            )
        )
        rows.append(
            _record(
                "SleepAnalysis",
                SLEEP_APP,
                bed + timedelta(minutes=30),
                bed + timedelta(hours=7, minutes=30),
                "HKCategoryValueSleepAnalysisInBed",
            )
        )  # overlap
        cursor = bed + timedelta(minutes=15)
        for stage in ["Core", "Deep", "Core", "REM", "Core", "Deep", "Core", "REM"]:
            length = timedelta(minutes=rng.randint(40, 55))
            rows.append(
                _record(
                    "SleepAnalysis",
                    SLEEP_APP,
                    cursor,
                    cursor + length,
                    f"HKCategoryValueSleepAnalysisAsleep{stage}",
                )
            )
            cursor += length
        rows.append(
            _record(
                "SleepAnalysis",
                SLEEP_APP,
                cursor,
                cursor + timedelta(minutes=3),
                "HKCategoryValueSleepAnalysisAwake",
            )
        )
        if i == GLITCH_NIGHT:  # app session never stopped: 20 hours "in bed"
            rows.append(
                _record(
                    "SleepAnalysis",
                    SLEEP_APP,
                    bed,
                    bed + timedelta(hours=20),
                    "HKCategoryValueSleepAnalysisInBed",
                )
            )

    rows.extend(rows[:5])  # exact duplicates, as written by a sync glitch
    return rows


def write_export_zip(path: str | Path, seed: int = 42) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    export_date = datetime.combine(FIRST_DAY + timedelta(days=DAYS), datetime.min.time())
    xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<!-- SYNTHETIC Apple Health export. All values are invented. -->",
            '<HealthData locale="en_GB" synthetic="true">',  # checked by the privacy guardrail
            f' <ExportDate value="{_ts(export_date)}"/>',
            *build_records(seed),
            "</HealthData>",
        ]
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("apple_health_export/export.xml", xml)
        archive.writestr("apple_health_export/export_cda.xml", "<ClinicalDocument/>")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Write a synthetic Apple Health export zip.")
    parser.add_argument("zip_path", type=Path)
    print(f"Synthetic export written: {write_export_zip(parser.parse_args().zip_path)}")


if __name__ == "__main__":
    main()
