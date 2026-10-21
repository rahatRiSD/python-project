import re
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from rapidfuzz import fuzz, process

APP_TITLE = "SurnameMatch — Celebrity Finder"
DEFAULT_CSV = Path(__file__).with_name("celebrities.csv")

st.set_page_config(page_title=APP_TITLE, page_icon="🔎", layout="wide")

# Common name endings that should not be treated as surnames.
SUFFIXES = {"jr", "jr.", "sr", "sr.", "ii", "iii", "iv", "v"}
PARTICLES = {"da", "de", "del", "della", "der", "di", "dos", "du",
             "la", "le", "van", "von", "bin", "al"}

SAMPLE_ROWS = [
    {"full_name": "Lionel Messi", "profession": "Footballer", "country": "Argentina"},
    {"full_name": "Cristiano Ronaldo", "profession": "Footballer", "country": "Portugal"},
    {"full_name": "Tom Cruise", "profession": "Actor", "country": "United States"},
    {"full_name": "Penélope Cruz", "profession": "Actor", "country": "Spain"},
    {"full_name": "Taylor Swift", "profession": "Singer", "country": "United States"},
    {"full_name": "Will Smith", "profession": "Actor", "country": "United States"},
    {"full_name": "Jaden Smith", "profession": "Actor / Singer", "country": "United States"},
    {"full_name": "Serena Williams", "profession": "Tennis player", "country": "United States"},
    {"full_name": "Venus Williams", "profession": "Tennis player", "country": "United States"},
    {"full_name": "Robert Downey Jr.", "profession": "Actor", "country": "United States"},
    {"full_name": "Zendaya", "profession": "Actor / Singer", "country": "United States"},
    {"full_name": "Ariana Grande", "profession": "Singer", "country": "United States"},
    {"full_name": "Jackie Chan", "profession": "Actor", "country": "Hong Kong"},
    {"full_name": "Keanu Reeves", "profession": "Actor", "country": "Canada"},
    {"full_name": "Benedict Cumberbatch", "profession": "Actor", "country": "United Kingdom"},
    {"full_name": "Emma Watson", "profession": "Actor", "country": "United Kingdom"},
    {"full_name": "Lewis Hamilton", "profession": "Racing driver", "country": "United Kingdom"},
    {"full_name": "Novak Djokovic", "profession": "Tennis player", "country": "Serbia"},
    {"full_name": "Kylian Mbappé", "profession": "Footballer", "country": "France"},
    {"full_name": "Virat Kohli", "profession": "Cricketer", "country": "India"},
    {"full_name": "Shah Rukh Khan", "profession": "Actor", "country": "India"},
    {"full_name": "Aamir Khan", "profession": "Actor", "country": "India"},
    {"full_name": "Priyanka Chopra", "profession": "Actor", "country": "India"},
    {"full_name": "Dwayne Johnson", "profession": "Actor / Wrestler", "country": "United States"},
    {"full_name": "Michael Jordan", "profession": "Basketball player", "country": "United States"},
    {"full_name": "Michael B. Jordan", "profession": "Actor", "country": "United States"},
    {"full_name": "Tom Holland", "profession": "Actor", "country": "United Kingdom"},
    {"full_name": "Chris Evans", "profession": "Actor", "country": "United States"},
    {"full_name": "Chris Hemsworth", "profession": "Actor", "country": "Australia"},
    {"full_name": "Scarlett Johansson", "profession": "Actor", "country": "United States"},
    {"full_name": "Billie Eilish", "profession": "Singer", "country": "United States"},
    {"full_name": "Ed Sheeran", "profession": "Singer", "country": "United Kingdom"},
    {"full_name": "Bruno Mars", "profession": "Singer", "country": "United States"},
    {"full_name": "Sadio Mané", "profession": "Footballer", "country": "Senegal"},
    {"full_name": "Mohamed Salah", "profession": "Footballer", "country": "Egypt"},
    {"full_name": "Neymar Jr.", "profession": "Footballer", "country": "Brazil"},
]

def normalize(text):
    """Lowercase and remove punctuation while preserving Unicode letters/digits."""
    text = str(text or "").casefold().strip()
    text = re.sub(r"[^\w\s'-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()

def get_surname(full_name):
    """Extract a best-effort surname, including common multiword surname particles."""
    tokens = normalize(full_name).replace("-", " ").split()
    if not tokens:
        return ""
    while tokens and tokens[-1].rstrip(".") in {s.rstrip(".") for s in SUFFIXES}:
        tokens.pop()
    if not tokens:
        return ""
    surname_tokens = [tokens[-1]]
    i = len(tokens) - 2
    while i >= 0 and tokens[i] in PARTICLES:
        surname_tokens.insert(0, tokens[i])
        i -= 1
    return " ".join(surname_tokens)

def prepare_database(df):
    """Validate columns and add normalized searchable fields."""
    if "full_name" not in df.columns:
        raise ValueError("CSV must contain a column named 'full_name'.")
    clean = df.copy()
    clean["full_name"] = clean["full_name"].fillna("").astype(str).str.strip()
    clean = clean[clean["full_name"] != ""].drop_duplicates(subset=["full_name"])
    if "profession" not in clean.columns:
        clean["profession"] = "Unknown"
    if "country" not in clean.columns:
        clean["country"] = "Unknown"
    clean["profession"] = clean["profession"].fillna("Unknown").astype(str)
    clean["country"] = clean["country"].fillna("Unknown").astype(str)
    clean["surname"] = clean["full_name"].map(get_surname)
    clean["surname_norm"] = clean["surname"].map(normalize)
    return clean.reset_index(drop=True)

def surname_search(query, df, limit=20, fuzzy_threshold=55):
    """
    SurnameMatch ranking:
    exact surname (100), prefix (90+), fuzzy similarity, then full-name similarity.
    Returns ranked candidates with an explainable match type.
    """
    q = normalize(query)
    if not q:
        return pd.DataFrame(columns=list(df.columns) + ["score", "match_type"])

    results = []
    surname_choices = df["surname_norm"].tolist()

    for idx, row in df.iterrows():
        surname = row["surname_norm"]
        full_name = normalize(row["full_name"])
        if not surname:
            continue

        if surname == q:
            score, match_type = 100.0, "Exact surname"
        elif surname.startswith(q):
            score, match_type = 90.0 + 9.0 * (len(q) / max(len(surname), 1)), "Surname starts with query"
        else:
            surname_score = fuzz.ratio(q, surname)
            partial_score = fuzz.partial_ratio(q, surname)
            best_fuzzy = max(surname_score, partial_score * 0.94)
            # A small secondary signal helps rank candidates when surname scores tie.
            if best_fuzzy >= fuzzy_threshold:
                score, match_type = best_fuzzy, "Fuzzy surname"
            else:
                # Full-name matching is intentionally weaker; it helps discover entries
                # with mononyms or unusual name formats without outranking surname matches.
                name_score = fuzz.ratio(q, full_name) * 0.72
                if name_score >= fuzzy_threshold:
                    score, match_type = name_score, "Possible name match"
                else:
                    continue

        results.append({
            **row.to_dict(),
            "score": round(float(score), 1),
            "match_type": match_type
        })

    if not results:
        # Suggest closest surnames so users can spot likely typos.
        unique_surnames = sorted(set(surname_choices))
        suggestions = process.extract(q, unique_surnames, scorer=fuzz.ratio, limit=5)
        return pd.DataFrame(columns=list(df.columns) + ["score", "match_type"]), suggestions

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        by=["score", "full_name"], ascending=[False, True]
    ).head(limit)
    return result_df, []

@st.cache_data
def load_default_data():
    if DEFAULT_CSV.exists():
        return pd.read_csv(DEFAULT_CSV)
    return pd.DataFrame(SAMPLE_ROWS)

st.title("🔎 SurnameMatch")
st.caption("Search celebrities using only a surname. Typo-tolerant ranking returns multiple candidates when names are shared.")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload celebrity CSV", type=["csv"])
    st.markdown("**Required column:** `full_name`")
    st.markdown("**Optional columns:** `profession`, `country`")
    st.divider()
    threshold = st.slider("Fuzzy-match threshold", min_value=40, max_value=90, value=55, step=5)
    max_results = st.slider("Maximum results", min_value=5, max_value=50, value=20, step=5)
    st.caption("Lower threshold finds more possible typos but can add false matches.")

try:
    raw_df = pd.read_csv(uploaded) if uploaded is not None else load_default_data()
    database = prepare_database(raw_df)
except Exception as exc:
    st.error(f"Could not load the database: {exc}")
    st.stop()

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Celebrities indexed", f"{len(database):,}")
metric2.metric("Unique surnames", f"{database['surname_norm'].nunique():,}")
metric3.metric("Data source", "Uploaded CSV" if uploaded is not None else "Sample CSV")

query = st.text_input("Enter a surname", placeholder="Try Messi, Smith, Williams, or Smth")
search_clicked = st.button("Search celebrities", type="primary")

if query.strip():
    matches, suggestions = surname_search(query, database, limit=max_results, fuzzy_threshold=threshold)
    st.subheader(f"Results for “{query.strip()}”")
    if not matches.empty:
        display_cols = ["full_name", "surname", "profession", "country", "score", "match_type"]
        st.dataframe(
            matches[display_cols].rename(columns={
                "full_name": "Celebrity",
                "surname": "Detected surname",
                "profession": "Profession",
                "country": "Country",
                "score": "Match score",
                "match_type": "Match type"
            }),
            use_container_width=True,
            hide_index=True
        )
        exact_count = int((matches["match_type"] == "Exact surname").sum())
        st.info(f"Found {len(matches)} ranked result(s), including {exact_count} exact surname match(es). Scores are ranking indicators, not probabilities.")
        chart_col, info_col = st.columns([3, 2])
        with chart_col:
            fig, ax = plt.subplots(figsize=(8, 3.6))
            plot_df = matches.head(10).sort_values("score", ascending=True)
            ax.barh(plot_df["full_name"], plot_df["score"])
            ax.set_xlabel("Match score (higher is better)")
            ax.set_title("Top celebrity surname matches")
            ax.set_xlim(0, 105)
            fig.tight_layout()
            st.pyplot(fig, clear_figure=True)
        with info_col:
            st.markdown("**How the ranking works**")
            st.markdown(
                "1. Exact surname match gets the highest score.\n"
                "2. Surnames beginning with the query rank next.\n"
                "3. Typo-tolerant fuzzy similarity finds close spellings.\n"
                "4. Full-name similarity is a weaker fallback."
            )
        csv_bytes = matches[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button("Download results as CSV", data=csv_bytes,
                           file_name="surname_search_results.csv", mime="text/csv")
    else:
        st.warning("No matches passed the current threshold.")
        if suggestions:
            st.write("Closest surname suggestions:")
            st.write(", ".join(f"{name} ({score:.0f}%)" for name, score, _ in suggestions))
        st.caption("Try a shorter spelling, lower the fuzzy threshold, or check that your CSV includes full_name.")

with st.expander("View current database"):
    st.dataframe(database[["full_name", "surname", "profession", "country"]], use_container_width=True, hide_index=True)

with st.expander("Algorithm flow figure"):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    boxes = [
        (3, 8.2, 4, 1, "Input surname"),
        (3, 6.5, 4, 1, "Normalize query + database names"),
        (3, 4.8, 4, 1, "Exact / prefix / fuzzy comparison"),
        (3, 3.1, 4, 1, "Rank candidates and apply threshold"),
        (3, 1.4, 4, 1, "Display results + score chart"),
    ]
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    for x, y, w, h, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                    edgecolor="black", facecolor="white", linewidth=1.5))
        ax.text(x+w/2, y+h/2, label, ha="center", va="center", fontsize=10)
    for i in range(len(boxes)-1):
        x, y, w, h, _ = boxes[i]
        nx, ny, nw, nh, _ = boxes[i+1]
        ax.add_patch(FancyArrowPatch((x+w/2, y-0.08), (nx+nw/2, ny+nh+0.08),
                                     arrowstyle="-|>", mutation_scale=14, linewidth=1.3))
    ax.set_title("SurnameMatch algorithm workflow", fontsize=14)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.divider()
st.caption("Prototype limitation: surname extraction is best-effort. Some cultures use different name orders or mononyms; review and normalize your dataset for high-stakes or research use.")
