
# 🔎 SurnameMatch — Celebrity Surname Search Algorithm

**SurnameMatch** is a Python-based celebrity search application that allows users to find celebrities by entering only their surname. It supports exact matching, prefix matching, typo correction, ranked search results, and interactive visualizations.

For example, searching for `Smth` can return possible matches for `Smith`, such as Will Smith and Jaden Smith.

## ✨ Features

- 🔍 Search celebrities using only a surname
- ✏️ Typo-tolerant fuzzy matching
- 🏆 Rank results by matching score
- 📊 Interactive charts to visualize search results
- 📁 Upload large celebrity databases in CSV format
- 📥 Download search results as a CSV file
- 🎚️ Adjust the fuzzy-matching threshold
- 🌐 Interactive web interface powered by Streamlit

## 🧠 Algorithm Overview

SurnameMatch follows these steps:

1. **Input:** Accept a surname from the user.
2. **Normalization:** Convert text to lowercase and normalize punctuation and whitespace.
3. **Surname extraction:** Extract a best-effort surname from each celebrity's full name.
4. **Exact matching:** Prioritize exact surname matches.
5. **Prefix matching:** Identify surnames beginning with the query.
6. **Fuzzy matching:** Use string similarity to identify possible spelling mistakes.
7. **Ranking:** Sort candidates by matching score.
8. **Visualization:** Display results in a table and interactive dashboard.

### Matching Priority

| Matching Method | Description |
|---|---|
| Exact match | The query matches the surname exactly |
| Prefix match | The surname begins with the query |
| Fuzzy match | The surname has a similar spelling |
| Name fallback | A weaker full-name similarity match |

**Note:** Matching scores are ranking indicators, not calibrated probabilities.

## 🛠️ Technologies Used

- Python
- Pandas
- RapidFuzz
- Matplotlib
- Streamlit

## 📂 Project Structure

```text
SurnameMatch/
├── app.py
├── celebrities.csv
├── requirements.txt
├── algorithm_flowchart.png
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SurnameMatch.git
cd SurnameMatch
```

Replace `YOUR_USERNAME` with your GitHub username and `SurnameMatch` with your actual repository name if different.

### 2. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 📊 Dataset Format

The application accepts CSV files containing a `full_name` column.

Example:

```csv
full_name,profession,country
Lionel Messi,Footballer,Argentina
Will Smith,Actor,United States
Jaden Smith,Actor/Singer,United States
Tom Cruise,Actor,United States
Serena Williams,Tennis Player,United States
```

The `profession` and `country` columns are optional.

For larger datasets, upload your CSV through the application's sidebar.

## 🖼️ Algorithm Flowchart

The project includes an algorithm flowchart named `algorithm_flowchart.png`.

To display it in your GitHub README, keep the image in the repository root and add:

```markdown
![SurnameMatch Algorithm Flowchart](algorithm_flowchart.png)
```

## 🧪 Example Searches

| Search Query | Example Expected Results |
|---|---|
| `Messi` | Lionel Messi |
| `Smith` | Will Smith, Jaden Smith |
| `Williams` | Serena Williams, Venus Williams |
| `Smth` | Possible matches for Smith |
| `Cruise` | Tom Cruise |

Results depend on the contents of the loaded database and the configured matching threshold.

## 📈 Evaluation and Future Improvements

Potential future improvements include:

- Expanding the database with a reliable, legally usable celebrity dataset.
- Improving surname extraction for different cultures and naming conventions.
- Adding language-aware transliteration and spelling correction.
- Optimizing search for millions of records.
- Evaluating precision, recall, F1-score, ranking quality, and latency.
- Comparing the proposed ranking method with standard fuzzy-search baselines.

## ⚠️ Limitations

- The included celebrity dataset is a small demonstration dataset, not a comprehensive directory.
- Surname extraction is heuristic and may not work for every naming convention.
- Fuzzy matching can return false positives.
- The algorithm has not yet been established as scientifically novel; further evaluation and comparison are needed.

## 👨‍💻 Author

**Your Name**

GitHub: [YOUR_USERNAME](https://github.com/YOUR_USERNAME)

## 📄 License

Choose a license appropriate for your intended use and the data included in the repository. A software license does not automatically grant rights to third-party celebrity data.
