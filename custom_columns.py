"""
Defines all 213 custom-column extraction specs used by the /custom route.

Each entry in COLUMN_DEFS is a tuple:
    (col_name, display_label, group_name, extract_spec)

extract_spec is one of:
    ("meta",  eppi_field,    col_name)   -> extractor.retrieve_metadata(...)
    ("data",  attr_id_var,   col_name)   -> extractor.retrieve_data(...)
    ("ht",    attr_id_var,   col_name)   -> extractor.retrieve_ht(...)
    ("info",  attr_id_var,   col_name)   -> extractor.retrieve_info(...)
    ("df5",   df5_col_name)              -> column taken from make_dataframe_5 result
"""

from eefdata.src.attributeIDs import (
    admin_strand_output, countries, publication_type_output,
    student_age_output, study_realism_output,
    number_of_schools_intervention_output, number_of_schools_control_output,
    number_of_schools_total_output,
    num_of_class_int_output, num_of_class_cont_output, num_of_class_tot_output,
    part_assign_output, level_of_assignment_output,
    study_design_output, randomisation_details,
    int_name_output, intervention_description_output, intervention_objectives_output,
    int_training_provided_output, intervention_teaching_approach,
    int_appr_dig_tech, int_appr_par_or_comm_vol,
    intervention_time_output, intervention_delivery_output,
    int_dur_output, inte_freq_output, intervention_session_length_output,
    edu_setting_output, int_focus_output, int_impl_details, int_costs_reported,
    baseline_diff_output, comparability_output, comp_vars_rep,
    which_comp_vars_rep_output, clustering_output, student_gender,
    sample_size_output, sample_size_intervention_output, sample_size_control_output,
    sample_size_second_intervention_output, sample_size_third_intervention_output,
    samp_size_anal_int_output, samp_size_anal_cont_output,
    samp_size_anal_sec_int_output, samp_size_anal_sec_cont_output,
    attr_dropout_rep_output, treat_grp_attr, overall_perc_attr,
)

# ── helpers ──────────────────────────────────────────────────────────────────

def _outcome_group(suffix, group_label):
    """Generate the 16-column block for each outcome type."""
    s = suffix  # e.g. "tool", "red", "wri", "math", "sci", "fsm"
    return [
        (f"out_tit_{s}",          f"Title ({s})",           group_label, ("df5", f"out_tit_{s}")),
        (f"out_desc_{s}",         f"Description ({s})",     group_label, ("df5", f"out_desc_{s}")),
        (f"out_type_{s}",         f"Type ({s})",            group_label, ("df5", f"out_type_{s}")),
        (f"smd_{s}",              f"SMD ({s})",             group_label, ("df5", f"smd_{s}")),
        (f"se_{s}",               f"SE ({s})",              group_label, ("df5", f"se_{s}")),
        (f"ci_lower_{s}",         f"CI Lower ({s})",        group_label, ("df5", f"ci_lower_{s}")),
        (f"ci_upper_{s}",         f"CI Upper ({s})",        group_label, ("df5", f"ci_upper_{s}")),
        (f"out_measure_{s}",      f"Measure ({s})",         group_label, ("df5", f"out_measure_{s}")),
        (f"out_g1_n_{s}",         f"Group 1 N ({s})",       group_label, ("df5", f"out_g1_n_{s}")),
        (f"out_g1_mean_{s}",      f"Group 1 Mean ({s})",    group_label, ("df5", f"out_g1_mean_{s}")),
        (f"out_g1_sd_{s}",        f"Group 1 SD ({s})",      group_label, ("df5", f"out_g1_sd_{s}")),
        (f"out_g2_n_{s}",         f"Group 2 N ({s})",       group_label, ("df5", f"out_g2_n_{s}")),
        (f"out_g2_mean_{s}",      f"Group 2 Mean ({s})",    group_label, ("df5", f"out_g2_mean_{s}")),
        (f"out_g2_sd_{s}",        f"Group 2 SD ({s})",      group_label, ("df5", f"out_g2_sd_{s}")),
        (f"out_test_type_raw_{s}",f"Test Type ({s})",       group_label, ("df5", f"out_test_type_raw_{s}")),
        (f"out_es_type_{s}",      f"ES Type ({s})",         group_label, ("df5", f"out_es_type_{s}")),
    ]


# ── master column list ────────────────────────────────────────────────────────

COLUMN_DEFS = [
    # General
    ("id",                "Study ID",                         "General",                    ("meta", "ItemId",    "id")),
    ("pub_author",        "Author",                           "General",                    ("meta", "ShortTitle","pub_author")),
    ("pub_year",          "Year",                             "General",                    ("meta", "Year",      "pub_year")),
    ("abstract",          "Abstract",                         "General",                    ("meta", "Abstract",  "abstract")),
    ("strand_raw",        "Admin Strand",                     "General",                    ("data", admin_strand_output,      "strand_raw")),
    ("loc_country_raw",   "Country",                          "General",                    ("data", countries,                "loc_country_raw")),
    ("pub_eppi",          "Publication Type (EPPI)",          "General",                    ("meta", "TypeName",  "pub_eppi")),
    ("pub_type_raw",      "Publication Type",                 "General",                    ("data", publication_type_output,  "pub_type_raw")),
    ("part_age_raw",      "Student Age",                      "General",                    ("data", student_age_output,       "part_age_raw")),
    ("eco_valid_raw",     "Ecological Validity",              "General",                    ("data", study_realism_output,     "eco_valid_raw")),
    # Number of Schools
    ("school_treat_info", "Schools Int (info)",               "Number of Schools",          ("info", number_of_schools_intervention_output, "school_treat_info")),
    ("school_treat_ht",   "Schools Int (ht)",                 "Number of Schools",          ("ht",   number_of_schools_intervention_output, "school_treat_ht")),
    ("school_cont_info",  "Schools Ctrl (info)",              "Number of Schools",          ("info", number_of_schools_control_output,      "school_cont_info")),
    ("school_cont_ht",    "Schools Ctrl (ht)",                "Number of Schools",          ("ht",   number_of_schools_control_output,      "school_cont_ht")),
    ("school_total_info", "Schools Total (info)",             "Number of Schools",          ("info", number_of_schools_total_output,        "school_total_info")),
    ("school_total_ht",   "Schools Total (ht)",               "Number of Schools",          ("ht",   number_of_schools_total_output,        "school_total_ht")),
    # Number of Classes
    ("class_treat_info",  "Classes Int (info)",               "Number of Classes",          ("info", num_of_class_int_output,  "class_treat_info")),
    ("class_treat_ht",    "Classes Int (ht)",                 "Number of Classes",          ("ht",   num_of_class_int_output,  "class_treat_ht")),
    ("class_cont_info",   "Classes Ctrl (info)",              "Number of Classes",          ("info", num_of_class_cont_output, "class_cont_info")),
    ("class_cont_ht",     "Classes Ctrl (ht)",                "Number of Classes",          ("ht",   num_of_class_cont_output, "class_cont_ht")),
    ("class_total_info",  "Classes Total (info)",             "Number of Classes",          ("info", num_of_class_tot_output,  "class_total_info")),
    ("class_total_ht",    "Classes Total (ht)",               "Number of Classes",          ("ht",   num_of_class_tot_output,  "class_total_ht")),
    # Participant Assignment
    ("part_assig_raw",    "Participant Assignment (raw)",      "Participant Assignment",     ("data", part_assign_output, "part_assig_raw")),
    ("part_assig_ht",     "Participant Assignment (ht)",       "Participant Assignment",     ("ht",   part_assign_output, "part_assig_ht")),
    ("part_assig_info",   "Participant Assignment (info)",     "Participant Assignment",     ("info", part_assign_output, "part_assig_info")),
    # Level of Assignment
    ("level_assig_raw",   "Level of Assignment (raw)",         "Level of Assignment",        ("data", level_of_assignment_output, "level_assig_raw")),
    ("level_assig_ht",    "Level of Assignment (ht)",          "Level of Assignment",        ("ht",   level_of_assignment_output, "level_assig_ht")),
    ("level_assig_info",  "Level of Assignment (info)",        "Level of Assignment",        ("info", level_of_assignment_output, "level_assig_info")),
    # Study Design
    ("int_desig_raw",     "Study Design (raw)",                "Study Design",               ("data", study_design_output, "int_desig_raw")),
    ("int_design_ht",     "Study Design (ht)",                 "Study Design",               ("ht",   study_design_output, "int_design_ht")),
    ("int_design_info",   "Study Design (info)",               "Study Design",               ("info", study_design_output, "int_design_info")),
    # Randomisation
    ("rand_raw",          "Randomisation (raw)",               "Randomisation",              ("data", randomisation_details, "rand_raw")),
    ("rand_ht",           "Randomisation (ht)",                "Randomisation",              ("ht",   randomisation_details, "rand_ht")),
    ("rand_info",         "Randomisation (info)",              "Randomisation",              ("info", randomisation_details, "rand_info")),
]

# Append the 6 × 16 outcome blocks
for _suffix, _label in [
    ("tool", "Toolkit Primary Outcome"),
    ("red",  "Reading Outcome"),
    ("wri",  "Writing Outcome"),
    ("math", "Math Outcome"),
    ("sci",  "Science Outcome"),
    ("fsm",  "FSM Outcome"),
]:
    COLUMN_DEFS.extend(_outcome_group(_suffix, _label))

COLUMN_DEFS += [
    # Intervention Details
    ("int_name_ht",            "Intervention Name (ht)",          "Intervention Details",  ("ht",   int_name_output,                    "int_name_ht")),
    ("int_name_info",          "Intervention Name (info)",         "Intervention Details",  ("info", int_name_output,                    "int_name_info")),
    ("int_desc_ht",            "Description (ht)",                 "Intervention Details",  ("ht",   intervention_description_output,    "int_desc_ht")),
    ("int_desc_info",          "Description (info)",               "Intervention Details",  ("info", intervention_description_output,    "int_desc_info")),
    ("int_objec_ht",           "Objectives (ht)",                  "Intervention Details",  ("ht",   intervention_objectives_output,     "int_objec_ht")),
    ("int_objec_info",         "Objectives (info)",                "Intervention Details",  ("info", intervention_objectives_output,     "int_objec_info")),
    ("int_training_raw",       "Training Provided (raw)",          "Intervention Details",  ("data", int_training_provided_output,       "int_training_raw")),
    ("int_training_ht",        "Training Provided (ht)",           "Intervention Details",  ("ht",   int_training_provided_output,       "int_training_ht")),
    ("int_training_info",      "Training Provided (info)",         "Intervention Details",  ("info", int_training_provided_output,       "int_training_info")),
    ("int_approach_raw",       "Teaching Approach (raw)",          "Intervention Details",  ("data", intervention_teaching_approach,     "int_approach_raw")),
    ("int_approach_ht",        "Teaching Approach (ht)",           "Intervention Details",  ("ht",   intervention_teaching_approach,     "int_approach_ht")),
    ("int_approach_info",      "Teaching Approach (info)",         "Intervention Details",  ("info", intervention_teaching_approach,     "int_approach_info")),
    ("digit_tech_raw",         "Digital Technology (raw)",         "Intervention Details",  ("data", int_appr_dig_tech,                  "digit_tech_raw")),
    ("digit_tech_ht",          "Digital Technology (ht)",          "Intervention Details",  ("ht",   int_appr_dig_tech,                  "digit_tech_ht")),
    ("digit_tech_info",        "Digital Technology (info)",        "Intervention Details",  ("info", int_appr_dig_tech,                  "digit_tech_info")),
    ("parent_partic_raw",      "Parental Engagement (raw)",        "Intervention Details",  ("data", int_appr_par_or_comm_vol,           "parent_partic_raw")),
    ("parent_partic_ht",       "Parental Engagement (ht)",         "Intervention Details",  ("ht",   int_appr_par_or_comm_vol,           "parent_partic_ht")),
    ("parent_partic_info",     "Parental Engagement (info)",       "Intervention Details",  ("info", int_appr_par_or_comm_vol,           "parent_partic_info")),
    ("int_when_raw",           "Intervention Timing (raw)",        "Intervention Details",  ("data", intervention_time_output,           "int_when_raw")),
    ("int_when_ht",            "Intervention Timing (ht)",         "Intervention Details",  ("ht",   intervention_time_output,           "int_when_ht")),
    ("int_when_info",          "Intervention Timing (info)",       "Intervention Details",  ("info", intervention_time_output,           "int_when_info")),
    ("int_who_raw",            "Intervention Delivery (raw)",      "Intervention Details",  ("data", intervention_delivery_output,       "int_who_raw")),
    ("int_who_ht",             "Intervention Delivery (ht)",       "Intervention Details",  ("ht",   intervention_delivery_output,       "int_who_ht")),
    ("int_who_info",           "Intervention Delivery (info)",     "Intervention Details",  ("info", intervention_delivery_output,       "int_who_info")),
    ("int_dur_ht",             "Duration (ht)",                    "Intervention Details",  ("ht",   int_dur_output,                     "int_dur_ht")),
    ("int_dur_info",           "Duration (info)",                  "Intervention Details",  ("info", int_dur_output,                     "int_dur_info")),
    ("int_leng_ht",            "Session Length (ht)",              "Intervention Details",  ("ht",   intervention_session_length_output, "int_leng_ht")),
    ("int_leng_info",          "Session Length (info)",            "Intervention Details",  ("info", intervention_session_length_output, "int_leng_info")),
    ("int_setting_raw",        "Setting (raw)",                    "Intervention Details",  ("info", edu_setting_output,                 "int_setting_raw")),
    ("int_setting_ht",         "Setting (ht)",                     "Intervention Details",  ("ht",   edu_setting_output,                 "int_setting_ht")),
    ("int_setting_info",       "Setting (info)",                   "Intervention Details",  ("info", edu_setting_output,                 "int_setting_info")),
    ("int_part_raw",           "Intervention Focus (raw)",         "Intervention Details",  ("info", int_focus_output,                   "int_part_raw")),
    ("int_part_ht",            "Intervention Focus (ht)",          "Intervention Details",  ("info", int_focus_output,                   "int_part_ht")),
    ("int_part_info",          "Intervention Focus (info)",        "Intervention Details",  ("info", int_focus_output,                   "int_part_info")),
    ("int_fidel_raw",          "Implementation Fidelity (raw)",    "Intervention Details",  ("data", int_impl_details,                   "int_fidel_raw")),
    ("int_fidel_ht",           "Implementation Fidelity (ht)",     "Intervention Details",  ("ht",   int_impl_details,                   "int_fidel_ht")),
    ("int_fidel_info",         "Implementation Fidelity (info)",   "Intervention Details",  ("info", int_impl_details,                   "int_fidel_info")),
    ("int_cost_raw",           "Costs Reported (raw)",             "Intervention Details",  ("data", int_costs_reported,                 "int_cost_raw")),
    ("int_cost_ht",            "Costs Reported (ht)",              "Intervention Details",  ("ht",   int_costs_reported,                 "int_cost_ht")),
    ("int_cost_info",          "Costs Reported (info)",            "Intervention Details",  ("info", int_costs_reported,                 "int_cost_info")),
    ("base_diff_raw",          "Baseline Differences (raw)",       "Intervention Details",  ("data", baseline_diff_output,               "base_diff_raw")),
    ("base_diff_ht",           "Baseline Differences (ht)",        "Intervention Details",  ("ht",   baseline_diff_output,               "base_diff_ht")),
    ("base_diff_info",         "Baseline Differences (info)",      "Intervention Details",  ("info", baseline_diff_output,               "base_diff_info")),
    ("comp_anal_raw",          "Comparability Analysis (raw)",     "Intervention Details",  ("data", comparability_output,               "comp_anal_raw")),
    ("comp_anal_ht",           "Comparability Analysis (ht)",      "Intervention Details",  ("ht",   comparability_output,               "comp_anal_ht")),
    ("comp_anal_info",         "Comparability Analysis (info)",    "Intervention Details",  ("info", comparability_output,               "comp_anal_info")),
    ("comp_var__raw",          "Comparability Vars (raw)",         "Intervention Details",  ("data", comp_vars_rep,                      "comp_var__raw")),
    ("comp_var__ht",           "Comparability Vars (ht)",          "Intervention Details",  ("ht",   comp_vars_rep,                      "comp_var__ht")),
    ("comp_var__info",         "Comparability Vars (info)",        "Intervention Details",  ("info", comp_vars_rep,                      "comp_var__info")),
    ("comp_var_rep_raw",       "Which Comp Vars (raw)",            "Intervention Details",  ("data", which_comp_vars_rep_output,         "comp_var_rep_raw")),
    ("comp_var_rep_ht",        "Which Comp Vars (ht)",             "Intervention Details",  ("ht",   which_comp_vars_rep_output,         "comp_var_rep_ht")),
    ("comp_var_rep_info",      "Which Comp Vars (info)",           "Intervention Details",  ("info", which_comp_vars_rep_output,         "comp_var_rep_info")),
    # Clustering
    ("clust_anal_raw",         "Clustering (raw)",                 "Clustering",            ("data", clustering_output, "clust_anal_raw")),
    ("clust_anal_ht",          "Clustering (ht)",                  "Clustering",            ("ht",   clustering_output, "clust_anal_ht")),
    ("clust_anal_info",        "Clustering (info)",                "Clustering",            ("info", clustering_output, "clust_anal_info")),
    # Student Gender
    ("part_gen_raw",           "Student Gender (raw)",             "Student Gender",        ("data", student_gender, "part_gen_raw")),
    ("part_gen_ht",            "Student Gender (ht)",              "Student Gender",        ("ht",   student_gender, "part_gen_ht")),
    ("part_gen_info",          "Student Gender (info)",            "Student Gender",        ("info", student_gender, "part_gen_info")),
    # Sample Sizes
    ("sample_analysed_ht",     "Sample Analysed (ht)",             "Sample Size",           ("ht",   sample_size_output,                     "sample_analysed_ht")),
    ("sample_analysed_info",   "Sample Analysed (info)",           "Sample Size",           ("info", sample_size_output,                     "sample_analysed_info")),
    ("base_n_treat_ht",        "Int Sample Size (ht)",             "Intervention Sample",   ("ht",   sample_size_intervention_output,         "base_n_treat_ht")),
    ("base_n_treat_info",      "Int Sample Size (info)",           "Intervention Sample",   ("info", sample_size_intervention_output,         "base_n_treat_info")),
    ("base_n_cont_ht",         "Ctrl Sample Size (ht)",            "Control Sample",        ("ht",   sample_size_control_output,              "base_n_cont_ht")),
    ("base_n_cont_info",       "Ctrl Sample Size (info)",          "Control Sample",        ("info", sample_size_control_output,              "base_n_cont_info")),
    ("base_n_treat2_ht",       "Int 2 Sample Size (ht)",           "Intervention 2 Sample", ("ht",   sample_size_second_intervention_output,  "base_n_treat2_ht")),
    ("base_n_treat2_info",     "Int 2 Sample Size (info)",         "Intervention 2 Sample", ("info", sample_size_second_intervention_output,  "base_n_treat2_info")),
    ("base_n_treat3_ht",       "Int 3 Sample Size (ht)",           "Intervention 3 Sample", ("ht",   sample_size_third_intervention_output,   "base_n_treat3_ht")),
    ("base_n_treat3_info",     "Int 3 Sample Size (info)",         "Intervention 3 Sample", ("info", sample_size_third_intervention_output,   "base_n_treat3_info")),
    ("n_treat_ht",             "Int Sample Analysed (ht)",         "Int Sample Analysed",   ("ht",   samp_size_anal_int_output,               "n_treat_ht")),
    ("n_treat_info",           "Int Sample Analysed (info)",       "Int Sample Analysed",   ("info", samp_size_anal_int_output,               "n_treat_info")),
    ("n_cont_ht",              "Ctrl Sample Analysed (ht)",        "Ctrl Sample Analysed",  ("ht",   samp_size_anal_cont_output,              "n_cont_ht")),
    ("n_cont_info",            "Ctrl Sample Analysed (info)",      "Ctrl Sample Analysed",  ("info", samp_size_anal_cont_output,              "n_cont_info")),
    ("n_treat2_ht",            "Int 2 Sample Analysed (ht)",       "Int 2 Sample Analysed", ("ht",   samp_size_anal_sec_int_output,            "n_treat2_ht")),
    ("n_treat2_info",          "Int 2 Sample Analysed (info)",     "Int 2 Sample Analysed", ("info", samp_size_anal_sec_int_output,            "n_treat2_info")),
    ("n_cont2_ht",             "Ctrl 2 Sample Analysed (ht)",      "Ctrl 2 Sample Analysed",("ht",   samp_size_anal_sec_cont_output,           "n_cont2_ht")),
    ("n_cont2_info",           "Ctrl 2 Sample Analysed (info)",    "Ctrl 2 Sample Analysed",("info", samp_size_anal_sec_cont_output,           "n_cont2_info")),
    # Attrition
    ("attri_raw",              "Attrition Reported (raw)",         "Attrition",             ("data", attr_dropout_rep_output, "attri_raw")),
    ("attri_ht",               "Attrition Reported (ht)",          "Attrition",             ("ht",   attr_dropout_rep_output, "attri_ht")),
    ("attri_info",             "Attrition Reported (info)",        "Attrition",             ("info", attr_dropout_rep_output, "attri_info")),
    ("attri_treat_ht",         "Attrition Treatment (ht)",         "Attrition",             ("ht",   treat_grp_attr,          "attri_treat_ht")),
    ("attri_treat_info",       "Attrition Treatment (info)",       "Attrition",             ("info", treat_grp_attr,          "attri_treat_info")),
    ("attri_perc_ht",          "Total % Attrition (ht)",           "Attrition",             ("ht",   overall_perc_attr,       "attri_perc_ht")),
    ("attri_perc_info",        "Total % Attrition (info)",         "Attrition",             ("info", overall_perc_attr,       "attri_perc_info")),
]

# ── derived structures ────────────────────────────────────────────────────────

# Ordered list of unique groups
GROUPS = list(dict.fromkeys(d[2] for d in COLUMN_DEFS))

# group -> [(col_name, display_label), ...]
COLUMN_GROUPS = {}
for col, label, group, _ in COLUMN_DEFS:
    COLUMN_GROUPS.setdefault(group, []).append((col, label))

# col_name -> extract_spec
EXTRACTORS = {col: spec for col, _, _, spec in COLUMN_DEFS}

# columns that require DataFrame 5
DF5_COLS = {col for col, _, _, spec in COLUMN_DEFS if spec[0] == "df5"}
