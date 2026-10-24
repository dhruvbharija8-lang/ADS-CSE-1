CONSTRUCTION PERMIT TIMELINES IN SAN FRANCISCO
ADS project data package | Prepared 23 October 2026, India time

Start with data/construction_permits_ssot.csv.gz (a gzip-compressed CSV).
In Google Colab or Python:
    import pandas as pd
    df = pd.read_csv("construction_permits_ssot.csv.gz", keep_default_na=False, na_values=[""], dtype={"permit_number": "string", "block": "string", "lot": "string", "parcel_block_key": "string", "parcel_lot_key": "string", "assessor_block": "string", "assessor_lot": "string", "assessor_parcel_number": "string", "record_id": "string", "assessor_row_id": "string", "zipcode": "string"})

WHAT IS INCLUDED
154,689 unique primary-address permit records filed 2019-2024. The integrated
file has 95 columns. This is a construction-related administrative dataset,
including alterations and signs; it is not 154,689 distinct construction sites.
No Kaggle records, simulated observations, padded rows or fabricated variables.

SOURCES
1. SF Department of Building Inspection, Building Permits, i98e-djp9:
   https://data.sf.gov/d/i98e-djp9
   Filter primary_address_flag='Y' and filed_date from 2019-01-01 through 2024-12-31.
   This reproduces the publisher's primary-address selection in f2jc-ivnc while
   retaining newer columns available in the underlying dataset.
2. SF Office of the Assessor-Recorder, wv5m-vpq2:
   https://data.sf.gov/d/wv5m-vpq2
   Official rolls 2017-2022; 1,266,295 source rows inspected. The package retains
   only the 92,364 unique parcel-year rows used in the join, with 18 recorded
   columns. A metadata download manifest records the full official requests.
3. U.S. Bureau of Labor Statistics, CPI-U series CUUR0000SA0:
   https://www.bls.gov/cpi/data.htm
   72 monthly published observations, January 2019 through December 2024.
   Full API response and month-level table included.

JOIN AND UNITS
One row per unique permit_number. Left-join permits to assessor on block + lot
(as text) and closed_roll_year = filing year minus 2. This conservative lag uses
rolls whose fiscal period ended before filing. It is historical property context,
not a point-in-time model feature store: source records can be corrected later.
All 154,689 permit rows remain; 151,378 match assessor (97.8596%). 3,311 do not
match and remain missing. Do not fill unmatched properties with invented values.
Join BLS on filing year-month; all 72 months match. This is a many-to-one join,
not extra independent observations or a causal effect of inflation.
Costs are USD, duration is calendar days, assessor area is square feet.
95 columns = 55 original permit columns + 18 assessor columns + 2 BLS fields
+ 20 derived, integration and QA columns. See metadata/data_dictionary.csv.

MEASUREMENT LIMITS
Filing-to-issuance includes agency and applicant time and payment waits.
Completion date is administrative final inspection, not measured active work.
Revised cost is an updated estimate, not observed spending or cost overrun.
Current status cannot reconstruct historical backlog. Never call every missing
issuance date pending: some permits are cancelled or withdrawn.
issued_within_365_days measures recorded issuance, not a legal service target.
CPI adjustment is broad purchasing-power normalization, not a construction-cost
index. National CPI is not San Francisco-specific. Cost comparisons within year
and type are an important robustness check.
Raw values and missingness are retained. Negative chronology is flagged (18
records); invalid intervals are missing in derived duration columns. Extreme
but valid durations are retained. Never delete all IQR outliers automatically.
Assessor built year may combine original and later construction; zoning can
reflect the last sale. Parcel splits and condominium conversions can break joins.

REPRODUCE AND AUDIT
Install pandas and numpy. Run python code/prepare_dataset.py to reconstruct an
identical data table from frozen raw inputs. It writes a separate _rebuilt CSV.
The supplied source_download_manifest.json contains official URLs, filters,
retrieval timestamps and SHA-256 hashes of FULL downloaded responses. Those
response hashes are not hashes of the repackaged compressed subsets.
file_checksums.json contains the hashes of the files actually delivered.
The source APIs are live: future downloads may legitimately differ.
Read metadata/data_audit.json, audit_by_year.csv and missingness.csv first.
The initial summaries and figures demonstrate feasibility. The proposed
hypotheses still require formal analysis and sensitivity checks.

COURSE AND SUBMISSION
The one-page PDF follows all eight pre-submission headings. Fill group number,
member names and student IDs before printing. Use the companion research guide
for rationale, source comparisons, methods, limitations and viva preparation.
The course handout requires a public GitHub repository for the final project
and explicitly flags AI-generated code/plagiarism under UFM. Confirm permitted
use of this preparation aid; write, verify and explain your own final analysis.
No repository has been created or published on your behalf.
