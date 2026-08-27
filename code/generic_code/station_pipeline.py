"""Reusable pipeline for station EDA and yearly consolidation.

This module centralizes common notebook logic for:
- loading yearly station files
- normalizing columns
- creating per-year EDA summaries
- condensing rows to one row per station
- generating optional folium maps and JSON-ready exports
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

import pandas as pd

from .ContaminantManagerJSON import ContaminantManagerJSON


STATION_COLUMN_MAP_2019_FORWARD: dict[str, str] = {
    "Estacio": "station_number",
    "nom_cabina": "station_name",
    "codi_dtes": "station_code",
    "zqa": "aqzc",
    "codi_eoi": "eoi_code",
    "Longitud": "longitude",
    "Latitud": "latitude",
    "ubicacio": "location",
    "Codi_districte": "district_code",
    "Nom_districte": "district_name",
    "Codi_barri": "neighborhood_code",
    "Nom_barri": "neighborhood_name",
    "Clas_1": "class_1",
    "Clas_2": "class_2",
    "Codi_Contaminant": "contaminant_code",
}


@dataclass
class PipelinePaths:
    """Resolved paths required by the pipeline."""

    stations_folder: Path
    contaminants_json: Path
    map_output_folder: Path


@dataclass
class YearlyResult:
    """Container with outputs for a single year."""

    year: int
    raw_df: pd.DataFrame
    normalized_df: pd.DataFrame
    condensed_df: pd.DataFrame
    summary: dict[str, Any]
    map_path: str | None = None


def _is_station_file(filename: str) -> bool:
    return bool(re.fullmatch(r"20\d{2}_stations\.csv", filename))


def _extract_year(filename: str) -> int:
    return int(filename[:4])


def discover_station_years(stations_folder: str | Path) -> list[int]:
    """Return sorted years available in the stations folder."""

    folder = Path(stations_folder)
    if not folder.exists():
        raise FileNotFoundError(f"Stations folder does not exist: {folder}")

    years = [_extract_year(p.name) for p in folder.iterdir() if _is_station_file(p.name)]
    return sorted(years)


def load_station_year(stations_folder: str | Path, year: int) -> pd.DataFrame:
    """Load one station csv by year."""

    file_path = Path(stations_folder) / f"{year}_stations.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Station file not found for year {year}: {file_path}")

    return pd.read_csv(file_path)


def normalize_station_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize station columns to English names when possible."""

    return df.rename(columns=STATION_COLUMN_MAP_2019_FORWARD)


def summarize_station_df(df: pd.DataFrame) -> dict[str, Any]:
    """Build a compact EDA summary used by notebooks and logs."""

    summary: dict[str, Any] = {
        "shape": tuple(df.shape),
        "columns": df.columns.tolist(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    if "station_code" in df.columns:
        summary["stations_count"] = int(df["station_code"].nunique())

    if "contaminant_code" in df.columns:
        summary["contaminants_count"] = int(df["contaminant_code"].nunique())

    return summary


def _normalize_station_identifier_set(df: pd.DataFrame) -> set[str]:
    """Extract a stable station identifier set from available station columns."""

    station_col = None
    if "station_code" in df.columns:
        station_col = "station_code"
    elif "station_number" in df.columns:
        station_col = "station_number"
    elif "Estacio" in df.columns:
        station_col = "Estacio"

    if station_col is None:
        raise ValueError(
            "Cannot compare years. Missing station identifier column "
            "(expected one of: station_code, station_number, Estacio)."
        )

    station_values = df[station_col].dropna().astype(str).str.strip()
    return {value for value in station_values if value != ""}


def _normalize_contaminant_code_set(df: pd.DataFrame) -> set[int]:
    """Extract contaminant code set as integers when possible."""

    if "contaminant_code" not in df.columns:
        raise ValueError("Cannot compare years. Missing contaminant_code column.")

    codes: set[int] = set()
    for code in df["contaminant_code"].dropna().tolist():
        try:
            codes.add(int(float(code)))
        except (TypeError, ValueError):
            continue

    return codes


def compare_years(
    year_a: int,
    year_b: int,
    yearly_results: dict[int, YearlyResult],
    contaminants_json: str | Path | None = None,
) -> dict[str, Any]:
    """Compare two years and report stations/contaminants added or removed.

    By convention, "added" means present in year_b but not in year_a,
    and "removed" means present in year_a but not in year_b.
    """

    if year_a not in yearly_results:
        raise ValueError(f"Year {year_a} not present in yearly_results.")
    if year_b not in yearly_results:
        raise ValueError(f"Year {year_b} not present in yearly_results.")

    df_a = yearly_results[year_a].normalized_df
    df_b = yearly_results[year_b].normalized_df

    stations_a = _normalize_station_identifier_set(df_a)
    stations_b = _normalize_station_identifier_set(df_b)

    contaminants_a = _normalize_contaminant_code_set(df_a)
    contaminants_b = _normalize_contaminant_code_set(df_b)

    stations_added = sorted(stations_b - stations_a)
    stations_removed = sorted(stations_a - stations_b)

    contaminants_added_codes = sorted(contaminants_b - contaminants_a)
    contaminants_removed_codes = sorted(contaminants_a - contaminants_b)

    contaminants_added: list[dict[str, Any]] = []
    contaminants_removed: list[dict[str, Any]] = []

    if contaminants_json is not None:
        contaminant_manager = ContaminantManagerJSON(str(contaminants_json))

        for code in contaminants_added_codes:
            description = contaminant_manager.get_metadata_summary_by_code(code)
            contaminants_added.append(
                {
                    "code": code,
                    "description": description["description"] if description else "UNKNOWN",
                }
            )

        for code in contaminants_removed_codes:
            description = contaminant_manager.get_metadata_summary_by_code(code)
            contaminants_removed.append(
                {
                    "code": code,
                    "description": description["description"] if description else "UNKNOWN",
                }
            )
    else:
        contaminants_added = [{"code": c} for c in contaminants_added_codes]
        contaminants_removed = [{"code": c} for c in contaminants_removed_codes]

    return {
        "from_year": year_a,
        "to_year": year_b,
        "stations": {
            "added": stations_added,
            "removed": stations_removed,
            "added_count": len(stations_added),
            "removed_count": len(stations_removed),
        },
        "contaminants": {
            "added": contaminants_added,
            "removed": contaminants_removed,
            "added_count": len(contaminants_added),
            "removed_count": len(contaminants_removed),
        },
    }


def compare_years_sequence(
    years: list[int],
    yearly_results: dict[int, YearlyResult],
    contaminants_json: str | Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Compare each consecutive pair in a year list.

    Returns a dict where keys are "YYYY_to_YYYY" and values are compare_years outputs.
    """

    if len(years) < 2:
        return {}

    sorted_years = sorted(years)
    comparisons: dict[str, dict[str, Any]] = {}

    for i in range(1, len(sorted_years)):
        year_a = sorted_years[i - 1]
        year_b = sorted_years[i]
        key = f"{year_a}_to_{year_b}"
        comparisons[key] = compare_years(
            year_a=year_a,
            year_b=year_b,
            yearly_results=yearly_results,
            contaminants_json=contaminants_json,
        )

    return comparisons


def condense_station_rows(
    df: pd.DataFrame,
    contaminant_manager: ContaminantManagerJSON,
) -> pd.DataFrame:
    """Condense multiple rows per station into one row with contaminant lists."""

    required_columns = {"station_code", "contaminant_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            "Cannot condense station data. Missing required columns: "
            + ", ".join(sorted(missing))
        )

    # Keep one representative value per station for station-level fields.
    station_level_columns = [
        c for c in df.columns if c not in {"contaminant_code"}
    ]

    grouped = df.groupby("station_code", dropna=False, sort=True)

    base = grouped[station_level_columns].first().reset_index(drop=True)
    contaminant_codes = grouped["contaminant_code"].apply(list).reset_index(drop=True)

    base["contaminant_code"] = contaminant_codes

    def _codes_to_names(codes: list[Any]) -> list[str]:
        names: list[str] = []
        for code in codes:
            parsed_code = int(float(code)) if pd.notna(code) else None
            if parsed_code is None:
                names.append("UNKNOWN")
                continue
            data = contaminant_manager.get_metadata_summary_by_code(parsed_code)
            names.append(data["description"] if data else "UNKNOWN")
        return names

    base["contaminant_names"] = base["contaminant_code"].apply(_codes_to_names)
    return base


def _to_station_export_dict(condensed_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    export_data: dict[str, dict[str, Any]] = {}

    for _, row in condensed_df.iterrows():
        station_id = str(row["station_code"])
        export_data[station_id] = {
            col: row[col] for col in condensed_df.columns if col != "station_code"
        }

    return export_data


def _build_map_for_year(
    condensed_df: pd.DataFrame,
    map_path: Path,
    popup_columns: list[tuple[str, str]],
    zoom_start: int = 12,
) -> None:
    import folium

    if "latitude" not in condensed_df.columns or "longitude" not in condensed_df.columns:
        raise ValueError("Cannot build map. Required columns missing: latitude/longitude")

    m = folium.Map(
        location=[condensed_df["latitude"].mean(), condensed_df["longitude"].mean()],
        tiles="OpenStreetMap",
        zoom_start=zoom_start,
    )

    for _, row in condensed_df.iterrows():
        popup_html = [f"<div style='min-width: 350px;'><b>Station Code: {row['station_code']}</b><ul>"]
        for col, label in popup_columns:
            popup_html.append(f"<li><b><i>{label}</i></b> -- \"{row.get(col, 'N/A')}\"")
        popup_html.append("</ul></div>")

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup="".join(popup_html),
        ).add_to(m)

    map_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(map_path))


def run_station_pipeline(
    stations_folder: str | Path,
    contaminants_json: str | Path,
    years: list[int] | None = None,
    save_maps: bool = False,
    map_output_folder: str | Path | None = None,
    map_zoom_start: int = 12,
) -> dict[str, Any]:
    """Run the complete station pipeline for selected years.

    Returns a dictionary with:
    - years: processed years
    - yearly_results: dict[year, YearlyResult]
    - export_data: JSON-ready nested dict
    """

    stations_folder_path = Path(stations_folder)
    contaminants_json_path = Path(contaminants_json)

    if map_output_folder is None:
        map_output_folder_path = stations_folder_path.parents[2] / "code" / "interative_maps"
    else:
        map_output_folder_path = Path(map_output_folder)

    paths = PipelinePaths(
        stations_folder=stations_folder_path,
        contaminants_json=contaminants_json_path,
        map_output_folder=map_output_folder_path,
    )

    available_years = discover_station_years(paths.stations_folder)
    selected_years = years if years is not None else available_years

    missing_requested = sorted(set(selected_years) - set(available_years))
    if missing_requested:
        raise ValueError(f"Requested years not available: {missing_requested}")

    contaminant_manager = ContaminantManagerJSON(str(paths.contaminants_json))

    popup_columns = [
        ("station_name", "Station Name"),
        ("location", "Location"),
        ("district_code", "District Code"),
        ("district_name", "District Name"),
        ("neighborhood_code", "Neighborhood Code"),
        ("neighborhood_name", "Neighborhood Name"),
        ("class_1", "Station Class"),
        ("class_2", "Station Sub-Class"),
        ("longitude", "Longitude"),
        ("latitude", "Latitude"),
        ("contaminant_code", "Contaminants Codes"),
        ("contaminant_names", "Contaminants Names"),
    ]

    yearly_results: dict[int, YearlyResult] = {}
    export_data: dict[str, dict[str, dict[str, Any]]] = {}

    for year in selected_years:
        raw_df = load_station_year(paths.stations_folder, year)
        normalized_df = normalize_station_columns(raw_df)
        summary = summarize_station_df(normalized_df)
        condensed_df = condense_station_rows(normalized_df, contaminant_manager)

        map_path: str | None = None
        if save_maps:
            target_map = paths.map_output_folder / f"map_{year}.html"
            _build_map_for_year(
                condensed_df=condensed_df,
                map_path=target_map,
                popup_columns=popup_columns,
                zoom_start=map_zoom_start,
            )
            map_path = str(target_map)

        yearly_results[year] = YearlyResult(
            year=year,
            raw_df=raw_df,
            normalized_df=normalized_df,
            condensed_df=condensed_df,
            summary=summary,
            map_path=map_path,
        )

        export_data[str(year)] = _to_station_export_dict(condensed_df)

    return {
        "years": selected_years,
        "yearly_results": yearly_results,
        "export_data": export_data,
    }
