# User Guide

This guide describes what the EEF Toolkit Data Extractor produces, what information each extraction type captures, and why that information is relevant to Toolkit evidence synthesis. It is intended for researchers, analysts, and evidence officers who use the application to work with EPPI-Reviewer data.

---

## How the application works

The application reads a JSON file exported directly from EPPI-Reviewer — the platform used to code studies during evidence synthesis for the EEF Teaching and Learning Toolkit and Early Years Toolkit. Each extraction option produces a structured dataset (CSV) drawn from the coded fields in that export. No data is modified during extraction; the application reorganises and standardises what coders have already recorded.

---

## Extraction types

### 1. General Study Information

**What it captures**

Core bibliographic and study design information for every study in the dataset. This is typically the first extraction run and serves as the master reference sheet to which other extractions can be joined by study ID.

Key fields include:

- **Study identifier and author** — a unique ID (EPPI item ID) and short author citation for each study
- **Publication year and type** — the year of publication and the type of document (e.g. journal article, report, thesis)
- **Educational setting** — the setting in which the intervention took place (e.g. primary school, secondary school, early years)
- **Ecological validity** — whether the study was conducted under conditions representative of real-world educational practice
- **Study design** — the research design used (e.g. Randomised Controlled Trial, Quasi-experiment)
- **Randomisation** — whether and how participants were randomly assigned to conditions
- **Level of assignment** — whether randomisation or allocation was at the level of individual pupil, class, or school
- **Participant age and assignment** — the age range of participants and how they were assigned
- **Outcome type** — what kind of outcome was measured (e.g. academic attainment, wider outcomes)
- **Country** — the country in which the study was conducted
- **Toolkit strand** — which strand of the Toolkit the study was coded to
- **Number of schools** — counts of schools in the treatment group, control group, and total, including cases where school numbers were not reported
- **Number of classes** — equivalent counts at the class level

**Why it matters**

This extraction underpins the evidence base for each Toolkit strand. It enables analysts to quickly characterise the body of evidence — how many studies used randomised designs, what age groups are represented, and which countries the research comes from.

---

### 2. Participants and Schools

**What it captures**

Detailed information about the intervention itself and the participants involved in each study.

Key fields include:

- **Intervention name and description** — the name of the programme or approach and a description of what it involved
- **Intervention approach** — the broad pedagogical or delivery approach (e.g. structured programme, teacher-led, digital)
- **Who delivered the intervention** — the person or role responsible for delivery (e.g. class teacher, teaching assistant, external provider)
- **Intervention provider** — the organisation or body that developed or supplied the intervention
- **Intervention duration, length, and frequency** — how long each session lasted, over what period, and how often it was delivered
- **When the intervention was delivered** — timing within the school day or year
- **Intervention objectives** — the stated aims of the programme
- **Intervention fidelity** — whether and how fidelity to the intended delivery model was monitored or reported
- **Training** — what training was provided to those delivering the intervention
- **Participant characteristics** — information about the pupils involved, including any additional characteristics reported
- **Parent participation** — whether parents or carers were involved in the intervention
- **Digital technology** — whether digital technology formed part of the approach
- **Costs** — any reported costs associated with the intervention
- **EEF evaluation** — whether the study was commissioned or conducted by the EEF
- **Comparison analysis and variables** — details of the comparison condition and any variables used in analysis
- **Baseline differences** — whether baseline differences between groups were reported and accounted for
- **Clustering** — whether the analysis accounted for the clustered nature of educational data (e.g. pupils nested within schools)

**Why it matters**

This extraction provides the detail needed to understand what was actually done in each study — not just what the outcome was, but how the intervention was structured and delivered. It supports judgements about implementation quality and transferability to other contexts.

---

### 3. Sample Size

**What it captures**

Quantitative information about the number of participants in each study, including attrition.

Key fields include:

- **Treatment and control group sizes** — the number of participants in each group at baseline and at follow-up
- **Total sample analysed** — the number of participants included in the primary analysis
- **Attrition** — whether attrition was reported, the percentage of participants lost to follow-up, and attrition specific to the treatment group
- **Pupil gender** — breakdown of participant gender where reported
- **Free School Meals (FSM) eligibility** — the proportion of participants eligible for Free School Meals, used as a proxy for socioeconomic disadvantage; includes cases where this information was not available

**Why it matters**

Sample sizes directly affect the statistical power of a study and, in turn, the confidence that can be placed in its findings. Attrition data are particularly important: high dropout rates can introduce bias and undermine the validity of the results. FSM data allow analysts to assess the extent to which findings are relevant to disadvantaged pupils.

---

### 4. Effect Size A

**What it captures**

Raw outcome data and effect size inputs for the primary outcome measures in each study. This extraction captures the statistics needed to compute or verify effect sizes.

Key fields include:

- **Pre- and post-test means and standard deviations** — for both treatment and control groups, where reported
- **Gain scores** — mean gain and standard deviation for treatment and control groups
- **Sample sizes at outcome level** — the number of participants contributing to each outcome
- **Descriptive statistics type** — the type of statistics reported (e.g. means, adjusted means)
- **Follow-up data** — whether outcomes were measured at a follow-up point beyond the immediate post-test
- **Other outcome statistics** — any additional statistics reported for treatment or control groups

**Why it matters**

Effect sizes are the primary unit of evidence in the Toolkit. This extraction provides the raw inputs from which standardised mean differences (SMDs) are calculated, enabling analysts to reproduce, verify, or re-calculate effect sizes where needed.

---

### 5. Effect Size B

**What it captures**

Calculated effect sizes and associated statistics for each outcome, broken down by outcome type. This extraction captures the final effect size values used in Toolkit synthesis.

Outcome types covered include:

- **Toolkit (primary attainment outcome)**
- **Mathematics**
- **Reading**
- **Writing**
- **Science**
- **Free School Meals subgroup**

For each outcome type, the following are extracted:

- **Standardised Mean Difference (SMD)** — the headline effect size
- **Standard Error (SE)** — the precision of the effect size estimate
- **Confidence Interval (lower and upper bounds)** — the range within which the true effect is estimated to lie with 95% confidence
- **Outcome title and description** — what the outcome measure was
- **Outcome type and label** — classification of the outcome
- **Comparison** — the comparison condition used for this outcome
- **Test type** — the type of assessment or measure used
- **Sample** — the sample to which this outcome applies

**Why it matters**

Effect Size B contains the synthesised results used directly in Toolkit strand summaries. It enables strand-level meta-analysis and allows comparisons across studies within and between strands.

---

### 6. Main Analysis (Strand-Specific)

**What it captures**

A strand-specific extraction containing the variables most relevant to the particular pedagogical approach being reviewed. The content varies by strand — each strand has a tailored set of fields selected by the evidence team during coding frame development.

A strand must be selected before this extraction can be run.

**Why it matters**

Different Toolkit strands involve different types of interventions, and the variables that matter most differ accordingly. Strand-specific extractions allow analysts to examine the features that are theoretically or practically significant for a given approach — for example, grouping practices in Setting and Streaming, or incentive structures in Performance Pay.

---

### 7. Other Educational Outcomes

**What it captures**

Outcomes that fall outside the primary attainment measures captured in Effect Size B. This includes broader outcomes that studies may report alongside their headline results.

Key fields include:

- **Educational outcomes** — additional attainment or skills outcomes reported in the study
- **Teacher outcomes** — outcomes relating to teachers, such as professional practice or wellbeing
- **Understandings and attitudes** — outcomes relating to pupil or teacher attitudes, motivations, or understandings
- **Wider outcomes** — any other outcomes reported that do not fit the above categories
- **School composition** — reported information about the composition of the school or cohort

**Why it matters**

Interventions often produce effects beyond the primary outcome measure. This extraction ensures those broader effects are recorded and available for analysis, supporting a more complete picture of what an intervention achieves.

---

### 8. Study Security

**What it captures**

A security rating for each study based on the strength of its research design. Study security is a summary judgement of how much confidence can be placed in the causal claims a study makes.

**Why it matters**

Not all studies are equally rigorous. Study security ratings allow the evidence base to be filtered or weighted by methodological quality, which is central to how the Toolkit presents and interprets evidence.

---

### 9. Padlocks

**What it captures**

The padlock score for each Toolkit strand, which summarises the overall security of the evidence base for that strand. Padlocks are the primary visual indicator used in the Toolkit to communicate confidence in the evidence.

**How padlock scores are calculated**

Each strand begins with a base score of 5 padlocks. One padlock is deducted for each of the following criteria where the strand's evidence base is rated as high risk:

| Criterion | What it measures |
|---|---|
| % of studies published since 2000 | Whether the evidence is sufficiently recent |
| % of studies using a randomised design | Whether the evidence comes from rigorous experimental studies |
| % of studies with high ecological validity | Whether the findings are likely to apply in real classroom settings |
| % of studies with an independent evaluation | Whether the research was conducted independently of the intervention developer |
| Median percentage attrition (reported) | Whether dropout rates are low enough not to threaten the validity of the results |

Each criterion is rated Low, Medium, or High risk based on the distribution of values across studies in that strand. A High risk rating on any criterion results in a one-padlock deduction. Deductions are cumulative, and the score cannot fall below zero.

The final padlock score therefore ranges from 0 to 5, where 5 indicates the strongest and most consistent evidence base and lower scores indicate areas of greater uncertainty or methodological concern.

**Why it matters**

The padlock score is the most widely recognised element of the Toolkit's presentation of evidence. It provides a transparent, reproducible summary of evidence quality that is accessible to non-specialist audiences including school leaders and policymakers. This extraction allows analysts to review and verify the inputs and outputs of the padlock calculation for any strand.

---

### 10. References

**What it captures**

Full bibliographic reference information for every study in the dataset, suitable for citation or export to reference management software.

Key fields include:

- **Authors** — full author list
- **Title** — the title of the study
- **Year** — year of publication
- **Publisher, institution, journal volume, issue, and pages** — publication details as recorded in EPPI-Reviewer
- **DOI and URL** — digital identifiers where available
- **Abstract** — the study abstract as recorded

**Why it matters**

A complete reference list is an essential output of any systematic review process. This extraction produces a clean, structured record of all studies included in the evidence base, which can be used to compile reference lists, support reporting, or verify inclusion decisions.

---

## A note on highlighted text and coder comments

For most fields, the extraction includes not only the coded response (e.g. a category label such as "Randomised Controlled Trial") but also, where available:

- **Highlighted text** — the passage from the source document that the coder selected to support their coding decision
- **Coder comments** — any additional notes or free-text observations entered by the coder

These supplementary fields are included in the CSV download and provide the qualitative context behind each coded data point.
