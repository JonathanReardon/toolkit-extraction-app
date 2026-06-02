#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import json as json_module
import os
import re
import tempfile
import uuid

import mistune
import numpy as np

from flask import (
    Flask, flash, redirect, render_template,
    request, send_file, session, url_for,
)
from werkzeug.utils import secure_filename

import pandas as pd

from eefdata.src.funcs import (
    DataFrameCompilation,
    JSONDataExtractor,
    RiskofBias,
    StrandSpecificFrames,
)
from custom_columns import COLUMN_DEFS, COLUMN_GROUPS, EXTRACTORS, DF5_COLS, GROUPS

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

UPLOAD_FOLDER = tempfile.mkdtemp()

# token -> filepath  (persists across requests; cleared on server restart)
STUDY_FILES = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _save_uploaded_file(file):
    """Save an uploaded FileStorage, register in STUDY_FILES, store token in session."""
    token = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f"{token}_{filename}")
    file.save(filepath)
    STUDY_FILES[token] = filepath
    session["file_token"] = token
    session["file_name"] = file.filename
    return token, filepath


def _session_file():
    """Return (token, filepath, display_name) from session, or (None, None, None)."""
    token = session.get("file_token")
    if not token:
        return None, None, None
    filepath = STUDY_FILES.get(token)
    if not filepath or not os.path.exists(filepath):
        session.pop("file_token", None)
        session.pop("file_name", None)
        return None, None, None
    return token, filepath, session.get("file_name", "uploaded file")


@app.context_processor
def inject_session_file():
    _, _, name = _session_file()
    return {"session_file_name": name}


@app.template_filter("display_val")
def display_val(value):
    """Render a cell value (may be list, string, or NA) as a clean string."""
    if isinstance(value, list):
        parts = [str(v) for v in value if v and str(v).strip() not in ("NA", "")]
        return " | ".join(parts) if parts else None
    s = str(value).strip() if value is not None else ""
    return s if s and s != "NA" else None


# ── Shared route: clear session file ─────────────────────────────────────────

@app.route("/clear-file")
def clear_file():
    session.pop("file_token", None)
    session.pop("file_name", None)
    return redirect(request.args.get("next", url_for("index")))


@app.route("/load-file", methods=["POST"])
def load_file():
    next_url = request.form.get("next", url_for("index"))
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please select a file.")
        return redirect(next_url)
    if not file.filename.endswith(".json"):
        flash("Only .json files are supported.")
        return redirect(next_url)
    _save_uploaded_file(file)
    return redirect(next_url)


# ── Options ───────────────────────────────────────────────────────────────────

DATAFRAME_OPTIONS = {
    "1":  {"label": "1. General Study Info",             "filename": "DataFrame1.csv"},
    "2":  {"label": "2. Participants & Schools",          "filename": "DataFrame2.csv"},
    "3":  {"label": "3. Sample Size",                     "filename": "DataFrame3_SampleSize.csv"},
    "4":  {"label": "4. Effect Size A",                   "filename": "DataFrame4_EffectSizeA.csv"},
    "5":  {"label": "5. Effect Size B",                   "filename": "DataFrame5_EffectSizeB.csv"},
    "6":  {"label": "6. Main Analysis (strand-specific)", "filename": "DataFrame6_MainAnalysis.csv"},
    "7":  {"label": "7. Other Educational Outcomes",      "filename": "DataFrame7_OtherEduOut.csv"},
    "8":  {"label": "8. Study Security",                  "filename": "StudySecurity.csv"},
    "9":  {"label": "9. Padlocks",                        "filename": "Padlocks.csv"},
    "10": {"label": "10. References",                     "filename": "References.csv"},
}

STRAND_OPTIONS = {
    "1":  "Arts Participation",       "2":  "Behaviour Interventions",
    "3":  "Collaborative Learning",   "4":  "Extending School Time",
    "5":  "Feedback",                 "6":  "Homework",
    "7":  "Individualised Instruction","8": "Mentoring",
    "9":  "Mastery Learning",         "10": "Metacognition & Self Regulation",
    "11": "One to One Tuition",       "12": "Oral Language",
    "13": "Physical Activity",        "14": "Parental Engagement",
    "15": "Phonics",                  "16": "Performance Pay",
    "17": "Peer Tutoring",            "18": "Reading Comprehension",
    "19": "Reducing Class Size",      "20": "Repeating a Year",
    "21": "Social & Emotional Learning","22":"Setting/Streaming",
    "23": "Small Group Tuition",      "24": "Summer Schools",
    "25": "Teaching Assistants",      "26": "Within-Class Grouping",
    "27": "Early Literacy Approaches","28": "Early Numeracy Approaches",
    "29": "Earlier Starting Age",     "30": "Extra Hours",
    "31": "Play-Based Learning",
}


@app.route("/padlocks")
def padlocks_detail():
    _, filepath, _ = _session_file()
    if not filepath:
        flash("Please load a JSON file first.")
        return redirect(url_for("index"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        rob = RiskofBias(json_extractor)
        rob.compile()
        df, _ = rob.padlocks(save_file=False)

        # Serialise through JSON to normalise all pandas/numpy types to plain Python
        row = json_module.loads(df.to_json(orient="records"))[0]

        # Extra stats not kept in the padlocks output — compute from risk_of_bias_df
        # (padlocks() already coerced these columns to numeric in-place)
        rdf = rob.risk_of_bias_df
        extras = [
            ("sample_analysed_info", "total_pupil_number", "sum"),
            ("eco_valid_risk_value",  "mean_eco_valid_risk",  "mean"),
            ("school_treat_info",     "median_school_number", "median"),
            ("class_total_info",      "median_class_number",  "median"),
        ]
        for col, key, agg in extras:
            try:
                val = getattr(pd.to_numeric(rdf[col], errors="coerce"), agg)()
                row[key] = int(val) if key == "total_pupil_number" else round(float(val), 2)
            except Exception:
                row[key] = 0

        return render_template("padlocks.html", data=row)
    except Exception as exc:
        flash(f"Padlocks calculation failed: {exc}")
        return redirect(url_for("index"))


@app.route("/padlocks/download")
def padlocks_download():
    _, filepath, _ = _session_file()
    if not filepath:
        flash("Please load a JSON file first.")
        return redirect(url_for("index"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        rob = RiskofBias(json_extractor)
        rob.compile()
        df, _ = rob.padlocks(save_file=False)
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        return send_file(output, mimetype="text/csv", as_attachment=True,
                         download_name="Padlocks.csv")
    except Exception as exc:
        flash(f"Download failed: {exc}")
        return redirect(url_for("padlocks_detail"))


# ── Study Security ────────────────────────────────────────────────────────────

SECURITY_CRITERIA = [
    ("Publication Year",        "pub_year_risk_value"),
    ("Publication Type",        "pub_type_risk_value"),
    ("Participant Assignment",  "part_assig_risk_value"),
    ("Randomisation",           "rand_risk_value"),
    ("Outcome Test Type",       "out_test_type_raw_risk_value"),
    ("Ecological Validity",     "eco_valid_risk_value"),
    ("Intervention Delivery",   "int_who_raw_risk_value"),
    ("Schools (Treatment)",     "school_treat_risk_value"),
    ("Sample Size",             "sample_size_risk_value"),
    ("Classes (Total)",         "class_total_risk_value"),
    ("Outcome Evaluation",      "out_eval_risk_value"),
    ("Effect Size Type",        "out_es_type_risk_value"),
    ("Comparability Analysis",  "comp_anal_risk_value"),
    ("Attrition",               "attri_perc_info_risk_value"),
    ("Clustering Analysis",     "clust_anal_risk_value"),
]

def _risk_label(val):
    try:
        v = int(float(val))
    except (TypeError, ValueError):
        return "NA"
    return {1: "H", 2: "M", 3: "L"}.get(v, "NA")


@app.route("/study-security")
def study_security_detail():
    _, filepath, _ = _session_file()
    if not filepath:
        flash("Please load a JSON file first.")
        return redirect(url_for("index"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        rob = RiskofBias(json_extractor)
        rob.compile()
        rdf = rob.risk_of_bias_df

        n_studies = len(rdf)

        # Per-criterion H/M/L counts
        criteria_summary = []
        for label, col in SECURITY_CRITERIA:
            col_num = pd.to_numeric(rdf[col], errors="coerce")
            h = int((col_num == 1).sum())
            m = int((col_num == 2).sum())
            l = int((col_num == 3).sum())
            criteria_summary.append({"label": label, "H": h, "M": m, "L": l})

        # raw_total distribution
        totals = pd.to_numeric(rdf["raw_total"], errors="coerce").dropna()
        mean_total  = round(float(totals.mean()), 2)
        median_total = round(float(totals.median()), 2)
        max_possible = len(SECURITY_CRITERIA) * 3

        # Distribution buckets (raw_total as int)
        dist = totals.astype(int).value_counts().sort_index()
        dist_labels = [str(i) for i in dist.index.tolist()]
        dist_counts = dist.values.tolist()

        # Per-study table: author, year, raw_total, mean, and H/M/L for each criterion
        studies = []
        for _, row in rdf.iterrows():
            study = {
                "author":    row.get("pub_author", ""),
                "year":      row.get("pub_year", ""),
                "raw_total": row.get("raw_total", ""),
                "mean":      round(float(row.get("Mean", 0) or 0), 2),
            }
            for _, col in SECURITY_CRITERIA:
                study[col] = _risk_label(row.get(col))
            studies.append(study)

        return render_template(
            "study_security.html",
            n_studies=n_studies,
            mean_total=mean_total,
            median_total=median_total,
            max_possible=max_possible,
            criteria_summary=criteria_summary,
            dist_labels=dist_labels,
            dist_counts=dist_counts,
            studies=studies,
            criteria=SECURITY_CRITERIA,
        )
    except Exception as exc:
        flash(f"Study security calculation failed: {exc}")
        return redirect(url_for("index"))


@app.route("/study-security/download")
def study_security_download():
    _, filepath, _ = _session_file()
    if not filepath:
        flash("Please load a JSON file first.")
        return redirect(url_for("index"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        rob = RiskofBias(json_extractor)
        rob.compile()
        df = rob.risk_of_bias_df
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)
        return send_file(output, mimetype="text/csv", as_attachment=True,
                         download_name="StudySecurity.csv")
    except Exception as exc:
        flash(f"Download failed: {exc}")
        return redirect(url_for("study_security_detail"))


# ── Documentation ────────────────────────────────────────────────────────────

def _render_md(filename):
    path = os.path.join(os.path.dirname(__file__), "docs", filename)
    with open(path, "r", encoding="utf-8") as f:
        md_text = f.read()
    headings = []
    for line in md_text.splitlines():
        m = re.match(r'^(#{1,3})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            anchor = re.sub(r'[^\w\s-]', '', title.lower()).strip()
            anchor = re.sub(r'[\s]+', '-', anchor)
            headings.append({"level": level, "title": title, "anchor": anchor})
    return mistune.html(md_text), headings


@app.route("/docs")
def docs():
    content, headings = _render_md("documentation.md")
    return render_template("docs.html", content=content, headings=headings,
                           page_title="Technical Documentation")


@app.route("/guide")
def guide():
    content, headings = _render_md("user-guide.md")
    return render_template("docs.html", content=content, headings=headings,
                           page_title="User Guide")


# ── Standard extraction ───────────────────────────────────────────────────────

@app.route("/")
def index():
    console_data = session.pop("console_padlocks", None)
    return render_template("index.html", options=DATAFRAME_OPTIONS, strands=STRAND_OPTIONS,
                           console_padlocks=console_data)


@app.route("/design/a")
def design_a():
    return render_template("index_a.html", options=DATAFRAME_OPTIONS, strands=STRAND_OPTIONS)


@app.route("/design/b")
def design_b():
    return render_template("index_b.html", options=DATAFRAME_OPTIONS, strands=STRAND_OPTIONS)


@app.route("/design/c")
def design_c():
    return render_template("index_c.html", options=DATAFRAME_OPTIONS, strands=STRAND_OPTIONS)


@app.route("/extract", methods=["POST"])
def extract():
    option = request.form.get("option", "")
    if option not in DATAFRAME_OPTIONS:
        flash("Please select a valid extraction option.")
        return redirect(url_for("index"))

    strand = request.form.get("strand", "")
    clean_cols = request.form.get("clean_cols", "1") == "1"
    if option == "6" and strand not in STRAND_OPTIONS:
        flash("Please select a strand for the Main Analysis dataframe.")
        return redirect(url_for("index"))

    # Resolve file: new upload takes priority, then session
    file = request.files.get("file")
    if file and file.filename:
        if not file.filename.endswith(".json"):
            flash("Only .json files are supported.")
            return redirect(url_for("index"))
        _, filepath = _save_uploaded_file(file)
    else:
        _, filepath, _ = _session_file()
        if not filepath:
            flash("Please upload a JSON file.")
            return redirect(url_for("index"))

    try:
        json_extractor = JSONDataExtractor(filepath)
        dfc = DataFrameCompilation(json_extractor)

        if option == "1":
            df, _ = dfc.make_dataframe_1(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == "2":
            df, _ = dfc.make_dataframe_2(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == "3":
            df, _ = dfc.make_dataframe_3(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == "4":
            result = dfc.make_dataframe_4(save_file=False, verbose=False, clean_cols=clean_cols)
            df = result[0] if result else None
        elif option == "5":
            df, _ = dfc.make_dataframe_5(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == "6":
            ss = StrandSpecificFrames(json_extractor)
            ss_df = ss.strand_specific_df_selection(int(strand))
            df, _ = dfc.make_dataframe_6(ss_df, save_file=False)
        elif option == "7":
            result = dfc.make_dataframe_7(save_file=False, verbose=False, clean_cols=clean_cols)
            df = result[0] if result else None
        elif option == "8":
            rob = RiskofBias(json_extractor)
            rob.compile()
            df = rob.risk_of_bias_df
        elif option == "9":
            rob = RiskofBias(json_extractor)
            rob.compile()
            df, _ = rob.padlocks(save_file=False)
            print("\n" + "="*60)
            print("PADLOCK SCORES")
            print("="*60)
            print(df.to_string(index=False))
            print("="*60 + "\n")
            session["console_padlocks"] = df.to_dict(orient="records")
            flash("Padlock data printed to terminal and browser console.")
            return redirect(url_for("index"))
        elif option == "10":
            df, _ = dfc.make_references(save_file=False)

        if df is None:
            flash("Extraction returned no data.")
            return redirect(url_for("index"))

        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)

        if option == "6":
            strand_label = STRAND_OPTIONS[strand].replace(" ", "_").replace("/", "-")
            download_name = f"DataFrame6_{strand_label}.csv"
        else:
            download_name = DATAFRAME_OPTIONS[option]["filename"]

        return send_file(output, mimetype="text/csv", as_attachment=True,
                         download_name=download_name)

    except Exception as exc:
        flash(f"Extraction failed: {exc}")
        return redirect(url_for("index"))


# ── Custom column selection ───────────────────────────────────────────────────

@app.route("/custom", methods=["GET"])
def custom():
    return render_template("custom.html", groups=GROUPS, column_groups=COLUMN_GROUPS)


@app.route("/custom/extract", methods=["POST"])
def custom_extract():
    selected = request.form.getlist("cols")
    selected = [c for c in selected if c in EXTRACTORS]
    if not selected:
        flash("Please select at least one column.")
        return redirect(url_for("custom"))

    file = request.files.get("file")
    if file and file.filename:
        if not file.filename.endswith(".json"):
            flash("Only .json files are supported.")
            return redirect(url_for("custom"))
        _, filepath = _save_uploaded_file(file)
    else:
        _, filepath, _ = _session_file()
        if not filepath:
            flash("Please upload a JSON file.")
            return redirect(url_for("custom"))

    try:
        json_extractor = JSONDataExtractor(filepath)
        dfc = DataFrameCompilation(json_extractor)

        df5 = None
        if any(c in DF5_COLS for c in selected):
            result = dfc.make_dataframe_5(save_file=False, verbose=False)
            df5 = result[0] if result else None

        parts = []
        for col in selected:
            spec = EXTRACTORS[col]
            kind = spec[0]
            if kind == "meta":
                part = json_extractor.retrieve_metadata(spec[1], spec[2])
            elif kind == "data":
                part = json_extractor.retrieve_data(spec[1], spec[2])
            elif kind == "ht":
                part = json_extractor.retrieve_ht(spec[1], spec[2])
            elif kind == "info":
                part = json_extractor.retrieve_info(spec[1], spec[2])
            elif kind == "df5":
                if df5 is not None and spec[1] in df5.columns:
                    part = df5[[spec[1]]]
                else:
                    continue
            else:
                continue
            parts.append(part)

        if not parts:
            flash("Extraction returned no data.")
            return redirect(url_for("custom"))

        df = pd.concat(parts, axis=1)
        df.fillna("NA", inplace=True)

        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8-sig")
        output.seek(0)

        return send_file(output, mimetype="text/csv", as_attachment=True,
                         download_name="CustomExtraction.csv")

    except Exception as exc:
        flash(f"Extraction failed: {exc}")
        return redirect(url_for("custom"))


# ── Study browser ─────────────────────────────────────────────────────────────

@app.route("/study", methods=["GET"])
def study():
    token, _, _ = _session_file()
    return render_template("study.html", session_token=token)


@app.route("/study/upload", methods=["POST"])
def study_upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please select a file.")
        return redirect(url_for("study"))
    if not file.filename.endswith(".json"):
        flash("Only .json files are supported.")
        return redirect(url_for("study"))
    token, _ = _save_uploaded_file(file)
    return redirect(url_for("study_list", token=token))


@app.route("/study/list/<token>")
def study_list(token):
    filepath = STUDY_FILES.get(token)
    if not filepath or not os.path.exists(filepath):
        flash("Session expired. Please upload the file again.")
        return redirect(url_for("study"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        id_df     = json_extractor.retrieve_metadata(EXTRACTORS["id"][1],        EXTRACTORS["id"][2])
        author_df = json_extractor.retrieve_metadata(EXTRACTORS["pub_author"][1], EXTRACTORS["pub_author"][2])
        year_df   = json_extractor.retrieve_metadata(EXTRACTORS["pub_year"][1],   EXTRACTORS["pub_year"][2])
        strand_df = json_extractor.retrieve_data(    EXTRACTORS["strand_raw"][1], EXTRACTORS["strand_raw"][2])

        listing = pd.concat([id_df, author_df, year_df, strand_df], axis=1)
        listing.fillna("NA", inplace=True)
        studies = listing.to_dict("records")
        return render_template("study_list.html", studies=studies, token=token)
    except Exception as exc:
        flash(f"Failed to read file: {exc}")
        return redirect(url_for("study"))


@app.route("/study/view/<token>/<study_id>")
def study_view(token, study_id):
    filepath = STUDY_FILES.get(token)
    if not filepath or not os.path.exists(filepath):
        flash("Session expired. Please upload the file again.")
        return redirect(url_for("study"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        dfc = DataFrameCompilation(json_extractor)

        df5 = None
        parts = []
        for col, _, _, spec in COLUMN_DEFS:
            kind = spec[0]
            try:
                if kind == "meta":
                    part = json_extractor.retrieve_metadata(spec[1], spec[2])
                elif kind == "data":
                    part = json_extractor.retrieve_data(spec[1], spec[2])
                elif kind == "ht":
                    part = json_extractor.retrieve_ht(spec[1], spec[2])
                elif kind == "info":
                    part = json_extractor.retrieve_info(spec[1], spec[2])
                elif kind == "df5":
                    if df5 is None:
                        result = dfc.make_dataframe_5(save_file=False, verbose=False)
                        df5 = result[0] if result else None
                    if df5 is not None and spec[1] in df5.columns:
                        part = df5[[spec[1]]]
                    else:
                        continue
                else:
                    continue
                parts.append(part)
            except Exception:
                continue

        if not parts:
            flash("No data could be extracted from this file.")
            return redirect(url_for("study_list", token=token))

        full_df = pd.concat(parts, axis=1)
        full_df = full_df.loc[:, ~full_df.columns.duplicated()]
        full_df.fillna("NA", inplace=True)

        match = full_df[full_df["id"].astype(str) == str(study_id)]
        if match.empty:
            flash(f"Study ID '{study_id}' not found.")
            return redirect(url_for("study_list", token=token))

        row = match.iloc[0].to_dict()

        sections = []
        for group in GROUPS:
            fields = [
                {"label": label, "value": row.get(col_name, "NA"), "col": col_name}
                for col_name, label in COLUMN_GROUPS[group]
            ]
            filled = sum(1 for f in fields if display_val(f["value"]) is not None)
            sections.append({"group": group, "fields": fields, "filled": filled})

        study_info = {
            "id":     row.get("id", study_id),
            "author": display_val(row.get("pub_author", "")) or "Unknown",
            "year":   display_val(row.get("pub_year", "")) or "",
            "strand": display_val(row.get("strand_raw", "")) or "",
        }
        return render_template("study_detail.html",
                               study=study_info, sections=sections, token=token)
    except Exception as exc:
        flash(f"Extraction failed: {exc}")
        return redirect(url_for("study_list", token=token))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard", methods=["GET"])
def dashboard():
    token, _, _ = _session_file()
    return render_template("dashboard.html", session_token=token)


@app.route("/dashboard/upload", methods=["POST"])
def dashboard_upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("Please select a file.")
        return redirect(url_for("dashboard"))
    if not file.filename.endswith(".json"):
        flash("Only .json files are supported.")
        return redirect(url_for("dashboard"))
    token, _ = _save_uploaded_file(file)
    return redirect(url_for("dashboard_view", token=token))


@app.route("/dashboard/view/<token>")
def dashboard_view(token):
    filepath = STUDY_FILES.get(token)
    if not filepath or not os.path.exists(filepath):
        flash("Session expired. Please upload the file again.")
        return redirect(url_for("dashboard"))
    try:
        json_extractor = JSONDataExtractor(filepath)
        dfc = DataFrameCompilation(json_extractor)

        result = dfc.make_dataframe_5(save_file=False, verbose=False)
        df5 = result[0] if result else None
        if df5 is None:
            flash("No effect size data found in this file.")
            return redirect(url_for("dashboard"))

        n_studies = len(df5)
        smd_cols = [c for c in df5.columns if c.startswith("smd_")]

        OUTCOME_LABELS = {
            "tool": "Toolkit Primary", "red": "Reading", "wri": "Writing",
            "math": "Maths", "sci": "Science", "fsm": "FSM",
        }
        by_type = {}
        all_values = []
        for col in smd_cols:
            suffix = col[4:]
            vals = pd.to_numeric(df5[col], errors="coerce").dropna().tolist()
            if vals:
                label = OUTCOME_LABELS.get(suffix, suffix)
                by_type[label] = vals
                all_values.extend(vals)

        if not all_values:
            flash("No numeric SMD values found in this file.")
            return redirect(url_for("dashboard"))

        arr = np.array(all_values)
        counts, edges = np.histogram(arr, bins=20)

        stats = {
            "n_studies":  n_studies,
            "n_outcomes": len(all_values),
            "mean":   round(float(np.mean(arr)),   3),
            "median": round(float(np.median(arr)), 3),
            "sd":     round(float(np.std(arr)),    3),
            "min":    round(float(np.min(arr)),    3),
            "max":    round(float(np.max(arr)),    3),
        }

        histogram     = json_module.dumps({"labels": [f"{e:.2f}" for e in edges[:-1]], "counts": counts.tolist()})
        by_type_counts = json_module.dumps({"labels": list(by_type.keys()), "counts": [len(v) for v in by_type.values()]})

        return render_template("dashboard_view.html",
                               stats=stats, histogram=histogram,
                               by_type_counts=by_type_counts, token=token)

    except Exception as exc:
        flash(f"Dashboard failed: {exc}")
        return redirect(url_for("dashboard"))


# ── Extraction preview pages ──────────────────────────────────────────────────

@app.route("/preview/<int:option>")
def preview(option):
    if option == 9:
        return redirect(url_for("padlocks_detail"))

    _, filepath, _ = _session_file()
    if not filepath:
        flash("Please load a JSON file first.")
        return redirect(url_for("index"))

    option_str = str(option)
    if option_str not in DATAFRAME_OPTIONS:
        flash("Invalid option.")
        return redirect(url_for("index"))

    strand_key = request.args.get("strand")
    # Default clean_cols to match function defaults (True for 4/5, False for others)
    clean_cols_default = option in (4, 5)
    clean_cols = request.args.get("clean_cols", "1" if clean_cols_default else "0") == "1"
    supports_clean_cols = option in (1, 2, 3, 4, 5, 7)

    if option == 6 and not strand_key:
        return render_template("preview.html",
                               records=None, columns=None,
                               option=option,
                               option_label=DATAFRAME_OPTIONS[option_str]["label"],
                               strand=None, strands=STRAND_OPTIONS,
                               needs_strand=True, row_count=0, col_count=0,
                               clean_cols=clean_cols,
                               supports_clean_cols=supports_clean_cols)

    try:
        json_extractor = JSONDataExtractor(filepath)
        dfc = DataFrameCompilation(json_extractor)

        if option == 1:
            df, _ = dfc.make_dataframe_1(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == 2:
            df, _ = dfc.make_dataframe_2(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == 3:
            df, _ = dfc.make_dataframe_3(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == 4:
            result = dfc.make_dataframe_4(save_file=False, verbose=False, clean_cols=clean_cols)
            df = result[0] if result else None
        elif option == 5:
            df, _ = dfc.make_dataframe_5(save_file=False, verbose=False, clean_cols=clean_cols)
        elif option == 6:
            ss = StrandSpecificFrames(json_extractor)
            ss_df = ss.strand_specific_df_selection(int(strand_key))
            df, _ = dfc.make_dataframe_6(ss_df, save_file=False)
        elif option == 7:
            result = dfc.make_dataframe_7(save_file=False, verbose=False, clean_cols=clean_cols)
            df = result[0] if result else None
        elif option == 8:
            rob = RiskofBias(json_extractor)
            rob.compile()
            df = rob.risk_of_bias_df
        elif option == 10:
            df, _ = dfc.make_references(save_file=False)
        else:
            flash("Unsupported option.")
            return redirect(url_for("index"))

        if df is None or df.empty:
            flash("Extraction returned no data.")
            return redirect(url_for("index"))

        records = json_module.loads(df.to_json(orient="records"))
        columns = list(df.columns)

        return render_template("preview.html",
                               records=records, columns=columns,
                               option=option,
                               option_label=DATAFRAME_OPTIONS[option_str]["label"],
                               strand=strand_key, strands=STRAND_OPTIONS,
                               needs_strand=False,
                               clean_cols=clean_cols,
                               supports_clean_cols=supports_clean_cols,
                               row_count=len(df), col_count=len(df.columns))

    except Exception as exc:
        flash(f"Preview failed: {exc}")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
