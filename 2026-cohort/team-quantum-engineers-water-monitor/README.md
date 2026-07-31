# 💧 AquaWatch Naija: Hyperlocal Water Quality Monitor Portal

![SDG](https://img.shields.io/badge/UN%20SDG-Goal%206%3A%20Clean%20Water%20%26%20Sanitation-0090CD)
![License](https://img.shields.io/badge/License-MIT-green)
![Built with](https://img.shields.io/badge/Built%20with-Python%20%7C%20Streamlit-1f425f)
![Status](https://img.shields.io/badge/Status-Cohort%20Submission%202026-orange)

**Team:** Quantum Engineers

**Team Members:** Alaisha Key, Douglas Phiri, Manahil Bashir, Nkechika Akpe, Sarah Davis

**UN SDG Goal:** Goal 6, Clean Water and Sanitation

---

## 📑 Table of Contents

1. [What AquaWatch Naija Does (and Why It Matters)](#what-it-does)
2. [Key Features](#key-features)
3. [Alignment with SDG 6](#sdg-alignment)
4. [Tech Stack](#tech-stack)
5. [Grow with Google Resources Used](#grow-with-google-resources)
6. [Research & Data](#research-data)
7. [Setup & Run Instructions](#setup-instructions)
8. [Video Walkthrough](#video-walkthrough)
9. [Implementation Plan](#implementation-plan)
10. [Future Ideas](#future-ideas)
11. [License](#license)

---

<a name="what-it-does"></a>
## 🎯 What AquaWatch Naija Does (and Why It Matters)

* **Problem Statement:** Community members lack a central, accessible public dashboard to view municipal water testing results and safety warnings.
* **Solution Summary:** AquaWatch Naija is a centralized, interactive web application designed to transform raw municipal water quality data into actionable, easy-to-understand insights. This project bridges the gap between complex public health data and everyday community awareness, empowering residents to monitor local safety levels and track historical sanitation metrics.

*"Naija" is a common, everyday nickname for Nigeria, used widely by Nigerians themselves. The name reflects that this dashboard is built for and by the communities it serves.*

---

<a name="key-features"></a>
## ✨ Key Features

| Feature | Description |
|---|---|
| **Interactive Dashboard** | Visualizes municipal water testing results in an accessible, non-technical format |
| **Year-Tagged Records** | Every test result is tagged by year, laying the groundwork for future trend analysis across testing periods |
| **Contamination Threshold Alerts** | Highlights when key safety indicators cross public health thresholds |
| **Data Standardization Pipeline** | Cleans and aggregates data from disparate municipal sources into one consistent schema |

---

<a name="sdg-alignment"></a>
## 🌍 Alignment with SDG 6

AquaWatch Naija directly supports **UN SDG 6: Clean Water and Sanitation** by:

* Increasing **public access to information** on local water safety. This is a core barrier to SDG 6 progress in underserved communities.
* Enabling **community accountability**, giving residents visibility into municipal testing results rather than relying on delayed or inaccessible official reports.
* Laying groundwork for **early-warning capability**, which is a stated milestone in SDG 6's sanitation and safe-water-management targets.

---

<a name="tech-stack"></a>
## 🛠️ Tech Stack

* **Language:** Python
* **Framework:** Streamlit (interactive dashboard/web app)
* **Data Processing:** Pandas-based cleaning, aggregation, and standardization pipeline
* **Data Sources:** Kaggle dataset plus two peer-reviewed academic case studies (see [Research & Data](#research-data) for full details)

---

<a name="grow-with-google-resources"></a>
## 🎓 Grow with Google Resources Used

The team collectively drew on the following Grow with Google Career Certificates to build, structure, and execute this project:

* Google Data Analytics Professional Certificate
* Google Advanced Data Analytics Professional Certificate
* Google IT Automation with Python Professional Certificate
* Google Cybersecurity Professional Certificate
* Google Digital Marketing & E-commerce Professional Certificate

---

<a name="research-data"></a>
## 📊 Research & Data

**Data Sources:**

* [Water Pollution and Disease dataset (Kaggle)](https://www.kaggle.com/datasets/khushikyad001/water-pollution-and-disease) by Khushi Yadav. Filtered to Nigeria-only records.
* Adejuwon, E. O., Ogwueleka, T. C., Ogungbemi, E. O., Prabhu, R., Rendon-Nava, A., and Yates, K. (2025). Assessment of Surface Water Quality Using Chemometric Tools: A Case Study of Jabi Lake, Abuja, Nigeria. Iranian Journal of Science and Technology, Transactions of Civil Engineering, 49, 829-852.
* Edegbene, A. O., Yandev, D., Omotehinwa, T. O., Zakaria, H., and Andy, B. O. (2025). Water quality assessment in Benue South, Nigeria: An investigation of physico-chemical and microbial characteristics. Water Science, 39(1), 279-290.

**Methodology:**

This project combines a national dataset with two peer-reviewed regional case studies to build a hyperlocal, Nigeria-specific water quality picture.

1. The Kaggle dataset (3,000 records across multiple countries) was filtered down to Nigeria-only records, producing an initial Nigeria dataset covering the regions South, Central, East, North, and West.
2. Water quality measurements from the two peer-reviewed case studies were extracted and standardized into a matching format:
   - The Jabi Lake study contributed the **Abuja (FCT)** region.
   - The Benue South study contributed the **Benue South** region.

   Note: "South" (from the Kaggle dataset) and "Benue South" (from the Benue South paper) are two distinct regions from two different sources. They are not the same and are kept separate in the dataset.
3. The Nigeria-filtered Kaggle data and the two case-study datasets were merged into a single finalized dataset, which powers the dashboard.

Data cleaning, metric standardization, and exploratory data analysis were used throughout to isolate key contamination thresholds and safety indicators for public consumption.

---

<a name="setup-instructions"></a>
## 🚀 Setup & Run Instructions

To clone the repository and run the project locally:

```bash
# Clone the repository
git clone https://github.com/MentorMeCollective/grow-with-google-showcase.git

# Navigate to the assigned team directory
cd 2026-cohort/team-quantum-engineers-water-monitor

# Check out our team's working branch
git checkout team-quantum-engineers

# Move into the src folder (app.py and the data file live here together)
cd src

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

---

<a name="video-walkthrough"></a>
## 🎥 Video Walkthrough

* **Project Demonstration:** [Watch the 5-Minute Project Walkthrough](https://www.youtube.com/watch?v=placeholder) (Link will be updated upon video recording completion)

---

<a name="implementation-plan"></a>
## 🗺️ Implementation Plan

**Timeline:** July 15 to August 14, 2026 (BUILD Project window)

| Phase | Task | Status |
|---|---|---|
| Phase 1 | Source and clean data: filter Kaggle dataset to Nigeria, extract and standardize data from two peer-reviewed case studies, merge into final combined dataset | Complete |
| Phase 2 | Convert finalized dataset to CSV and build the Streamlit dashboard (filtering, risk classification, map, summary metrics, data table) | Upcoming |
| Phase 3 | Test the app locally, confirm setup instructions work end-to-end, finalize README and repo structure | Upcoming |
| Phase 4 | Record 5-minute project walkthrough video and link it in the README | Upcoming |
| Phase 5 | Final review and submission via pull request to `main` on the `team-quantum-engineers` branch | Upcoming |

**Resources:**

* **Data:** Kaggle dataset plus two peer-reviewed academic case studies (see [Research & Data](#research-data) for full details)
* **Tools:** Python, Streamlit, Pandas, NumPy
* **Team:** Five cross-functional Scholars collaborating together throughout, including joint working sessions for planning and development

**Risks & Mitigation:**

* **Data inconsistency across sources:** Since the dataset merges a general Kaggle dataset with two independently collected academic studies, column names and formats needed to be manually standardized before merging. This was addressed by aligning column names and units across all three sources before combining them into the final dataset.
* **Team members' unfamiliarity with Streamlit/GitHub:** Several team members are new to Streamlit and GitHub. Mitigated by working collaboratively through shared sessions and keeping setup instructions explicit for anyone following along.

---

<a name="future-ideas"></a>
## 💡 Future Ideas

* Add a year-over-year trend visualization (e.g., average contaminant and bacteria levels by year) to surface long-term sanitation patterns, building on the year-tagged records already in the dataset.
* Expand data ingestion to incorporate real-time automated IoT sensor feeds from local water treatment facilities.
* Integrate an automated multi-language notification service to alert community residents via SMS regarding urgent water quality shifts.

---

<a name="license"></a>
## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

Copyright (c) 2026 Team Quantum Engineers
