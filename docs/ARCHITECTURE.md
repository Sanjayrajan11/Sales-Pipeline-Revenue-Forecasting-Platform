# Architecture

```mermaid
flowchart TD
A[Synthetic customers / opportunities / dated events] --> B[Raw Parquet and validation]
B --> C[Cleaning and quarantine]
C --> D[SQLite analytical warehouse]
D --> E[42 executable SQL questions]
E --> F[Python KPI / funnel / statistical analysis]
F --> G[Forecast / risk / scenario engines]
G --> H[Streamlit MERIDIAN application]
H --> I[Evidence-led business decisions]
C --> J[Quality audit and processed Parquet]
G --> K[CSV reports / interviews / portfolio evidence]
```

Physical execution calculates Python outputs before atomic database publication so all app tables appear together. SQL is then executed as a release gate against that complete warehouse. The diagram describes analytical responsibilities rather than separate services.

Customer 1→many Opportunities; Rep 1→many Opportunities; Team 1→many Reps; Product 1→many Opportunities; Opportunity 1→many Activities and Stage Visits; won Opportunity 1→1 Contract; Rep 1→many Monthly Targets. Region and industry are conformed descriptive attributes. Accounts map one-to-one to customers in this version.
