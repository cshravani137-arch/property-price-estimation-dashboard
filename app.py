from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "raw" / "india_property_sample.csv"
PUBLIC_PATH = BASE_DIR / "data" / "raw" / "public_listings_extract.csv"
SOURCES_PATH = BASE_DIR / "data" / "raw" / "sources.csv"

FEATURES = [
    "city", "locality", "property_type", "area_sqft", "bhk", "bathrooms",
    "age_years", "furnishing_status", "parking", "lift", "gated_community",
    "gym", "swimming_pool", "sale_year",
]
CATEGORICAL = ["city", "locality", "property_type", "furnishing_status"]
NUMERIC = [column for column in FEATURES if column not in CATEGORICAL]

st.set_page_config(
    page_title="PropertyLens | Indian Property Analytics",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Visual refresh: clean light canvas, deep navy navigation, teal accent, readable metrics.
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
      :root { --ink:#142235; --muted:#66758a; --teal:#0f766e; --line:#e4eaf1; --panel:#ffffff; }
      html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
      .stApp { background:#f5f7fb; color:var(--ink); }
      [data-testid="stHeader"] { background:rgba(245,247,251,.92); }
      .block-container { max-width:1440px; padding-top:1.7rem; padding-bottom:2.8rem; }
      [data-testid="stSidebar"] { background:#101e30; border-right:1px solid #20334a; }
      [data-testid="stSidebar"] * { color:#eef5fb; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { background:transparent; border-radius:10px; padding:7px 9px; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#20334a; }
      [data-testid="stSidebar"] hr { border-color:#314258; }
      .brand-mark { width:44px;height:44px;display:flex;align-items:center;justify-content:center;border-radius:14px;background:#d6f5ee;color:#0f766e;font-size:24px;margin-bottom:12px; }
      .brand-name { font-family:'Manrope',sans-serif;font-size:1.27rem;font-weight:800;letter-spacing:-.035em;line-height:1.1; }
      .brand-sub { color:#a6b7ca;font-size:.78rem;margin-top:6px; }
      .topline { color:#0f766e;font-size:.75rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.45rem; }
      .hero { background:linear-gradient(120deg,#122238 0%,#17485a 58%,#0f766e 100%); padding:1.8rem 2rem; border-radius:22px; color:white; margin:.4rem 0 1.05rem 0; box-shadow:0 12px 28px rgba(17,47,66,.12); }
      .hero h1 { color:white;font-family:'Manrope',sans-serif;font-size:clamp(1.7rem,3vw,2.5rem);line-height:1.12;letter-spacing:-.045em;margin:0 0 .65rem 0; }
      .hero p { color:#d9eaf0;font-size:1rem;max-width:760px;line-height:1.6;margin:0; }
      .hero-pill { display:inline-block;background:rgba(255,255,255,.12);color:#e8faf6;border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:5px 11px;font-size:.76rem;margin-bottom:14px; }
      .section-kicker { color:#0f766e;font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.13em;margin-bottom:.25rem; }
      .section-title { font-family:'Manrope',sans-serif;font-weight:800;letter-spacing:-.035em;font-size:1.32rem;margin:0 0 .25rem 0;color:#142235; }
      .muted { color:#66758a;font-size:.9rem; }
      div[data-testid="stMetric"] { background:#ffffff !important;border:1px solid #e4eaf1;border-radius:16px;padding:17px 18px;box-shadow:0 4px 16px rgba(23,43,66,.035); }
      /* Streamlit renders metric labels inside nested Markdown elements. Force contrast on
         the label and every descendant so theme styles cannot make the label nearly white. */
      div[data-testid="stMetric"] [data-testid="stMetricLabel"],
      div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
      div[data-testid="stMetric"] [data-testid="stMetricLabel"] p,
      div[data-testid="stMetric"] [data-testid="stMetricLabel"] svg {
        color:#52647a !important; fill:#52647a !important; stroke:#52647a !important;
        opacity:1 !important; visibility:visible !important; font-weight:700 !important;
      }
      div[data-testid="stMetric"] [data-testid="stMetricValue"],
      div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
        color:#142235 !important; opacity:1 !important; visibility:visible !important;
        font-family:'Manrope',sans-serif;font-weight:800;letter-spacing:-.04em;
      }
      div[data-testid="stMetric"] [data-testid="stMetricDelta"],
      div[data-testid="stMetric"] [data-testid="stMetricDelta"] * { color:#52647a !important; opacity:1 !important; }
      div[data-testid="stMetricLabel"] { color:#52647a !important;font-weight:700 !important; opacity:1 !important; }
      div[data-testid="stMetricValue"] { color:#142235 !important;font-family:'Manrope',sans-serif;font-weight:800;letter-spacing:-.04em;opacity:1 !important; }
      div[data-testid="stMetricDelta"] { font-size:.8rem; }
      /* Make ordinary controls readable in both light and dark browser themes. */
      div[data-testid="stSelectbox"] label,
      div[data-testid="stMultiSelect"] label,
      div[data-testid="stNumberInput"] label,
      div[data-testid="stSlider"] label,
      div[data-testid="stCheckbox"] label,
      div[data-testid="stRadio"] label,
      div[data-testid="stTextInput"] label,
      div[data-testid="stDateInput"] label,
      div[data-testid="stFileUploader"] label,
      div[data-testid="stWidgetLabel"] p {
        color:#26384d !important; opacity:1 !important; font-weight:600 !important;
      }
      div[data-testid="stButton"] > button,
      div[data-testid="stFormSubmitButton"] > button,
      div[data-testid="stDownloadButton"] > button,
      button[data-testid^="stBaseButton"] {
        color:#142235 !important; background:#ffffff !important;
        border:1px solid #cbd5e1 !important;
      }
      div[data-testid="stButton"] > button *,
      div[data-testid="stFormSubmitButton"] > button *,
      div[data-testid="stDownloadButton"] > button *,
      button[data-testid^="stBaseButton"] * { color:inherit !important; opacity:1 !important; }
      div[data-testid="stPlotlyChart"] { background:white;border:1px solid #e4eaf1;border-radius:16px;padding:7px; }
      div[data-testid="stDataFrame"] { border:1px solid #e4eaf1;border-radius:14px;overflow:hidden; }
      div[data-testid="stForm"] { background:white;border:1px solid #e4eaf1;border-radius:18px;padding:1.15rem 1.2rem; }
      .note { background:#eef7f5;border:1px solid #cce9e3;border-radius:12px;padding:12px 14px;color:#255e58;font-size:.87rem; }
      .warning-note { background:#fff8e8;border:1px solid #f4dfaa;border-radius:12px;padding:12px 14px;color:#785b16;font-size:.87rem; }
      .estimate-value { color:#0f766e;font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(2rem,4vw,3rem);letter-spacing:-.055em;line-height:1.1; }
      .estimate-panel { background:linear-gradient(135deg,#e8f8f3,#f5fbf9);border:1px solid #cce9e3;border-radius:20px;padding:1.4rem 1.5rem; }
      /* Make every Streamlit button fully readable, including long download labels. */
      div[data-testid="stButton"] > button,
      div[data-testid="stFormSubmitButton"] > button,
      div[data-testid="stDownloadButton"] > button,
      button[data-testid^="stBaseButton"] {
        box-sizing:border-box !important;
        min-height:44px !important;
        height:auto !important;
        max-width:100% !important;
        padding:.68rem 1rem !important;
        border-radius:10px !important;
        white-space:normal !important;
        overflow:visible !important;
        text-overflow:clip !important;
        line-height:1.35 !important;
        font-weight:700 !important;
        overflow-wrap:anywhere !important;
      }
      div[data-testid="stButton"] > button p,
      div[data-testid="stFormSubmitButton"] > button p,
      div[data-testid="stDownloadButton"] > button p,
      button[data-testid^="stBaseButton"] p,
      button[data-testid^="stBaseButton"] span {
        white-space:normal !important;
        overflow:visible !important;
        text-overflow:clip !important;
        height:auto !important;
        line-height:1.35 !important;
        overflow-wrap:anywhere !important;
      }
      div[data-testid="stButton"] > button[kind="primary"],
      div[data-testid="stFormSubmitButton"] > button[kind="primary"],
      div[data-testid="stDownloadButton"] > button[kind="primary"],
      div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"],
      div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primary"],
      div[data-testid="stDownloadButton"] > button[data-testid="stBaseButton-primary"] {
        background:#0f766e !important;
        color:#ffffff !important;
        border:1px solid #0f766e !important;
      }
      div[data-testid="stButton"] > button[kind="primary"] *,
      div[data-testid="stFormSubmitButton"] > button[kind="primary"] *,
      div[data-testid="stDownloadButton"] > button[kind="primary"] *,
      div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] *,
      div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primary"] *,
      div[data-testid="stDownloadButton"] > button[data-testid="stBaseButton-primary"] * {
        color:#ffffff !important;
      }
      div[data-testid="stButton"] > button[kind="primary"]:hover,
      div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
      div[data-testid="stDownloadButton"] > button[kind="primary"]:hover,
      button[data-testid="stBaseButton-primary"]:hover {
        background:#115e59 !important;border-color:#115e59 !important;
      }
      button:focus-visible { outline:3px solid #7dd3c7 !important; outline-offset:2px !important; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label {
        white-space:normal !important; overflow:visible !important; text-overflow:clip !important;
        min-height:38px; line-height:1.35; overflow-wrap:anywhere;
      }
      .footer { border-top:1px solid #e2e8f0;padding-top:14px;margin-top:30px;color:#77869a;font-size:.78rem; }
      @media(max-width:700px) {
        .block-container{padding:1rem .8rem 2rem .8rem}
        .hero{padding:1.3rem;border-radius:16px}
        div[data-testid="stButton"] > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button { width:100%; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def inr_grouping(number):
    """Format whole rupees using Indian comma placement."""
    try:
        number = int(round(float(number)))
    except (ValueError, TypeError):
        return "₹ —"
    sign = "-" if number < 0 else ""
    digits = str(abs(number))
    if len(digits) <= 3:
        formatted = digits
    else:
        last_three, rest = digits[-3:], digits[:-3]
        pairs = []
        while len(rest) > 2:
            pairs.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            pairs.insert(0, rest)
        formatted = ",".join(pairs + [last_three])
    return f"{sign}₹{formatted}"


def money_lakhs(lakhs, compact=True):
    rupees = float(lakhs) * 100_000
    if compact:
        if rupees >= 10_000_000:
            return f"₹{rupees / 10_000_000:.2f} Cr"
        if rupees >= 100_000:
            return f"₹{rupees / 100_000:.2f} L"
    return inr_grouping(rupees)


@st.cache_data(show_spinner=False)
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. From the project folder, run: python3 create_demo_data.py"
        )
    df = pd.read_csv(DATA_PATH)
    df.columns = [col.strip().lower() for col in df.columns]
    required = set(FEATURES + ["price_lakhs", "record_id"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    df = df.dropna(subset=FEATURES + ["price_lakhs"]).copy()
    df["price_lakhs"] = pd.to_numeric(df["price_lakhs"], errors="coerce")
    df = df[df["price_lakhs"] > 0].copy()
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in CATEGORICAL:
        df[col] = df[col].fillna("Unknown").astype(str)
    return df


@st.cache_resource(show_spinner="Training the demo price-estimation model…")
def train_model(data_signature):
    df = load_data()
    X, y = df[FEATURES], df["price_lakhs"]
    if len(df) < 20:
        raise ValueError("At least 20 valid records are required to train the demo model.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    preprocess = ColumnTransformer(
        [("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
         ("numbers", "passthrough", NUMERIC)],
        remainder="drop",
    )
    pipeline = Pipeline([
        ("preprocessor", preprocess),
        ("regressor", RandomForestRegressor(n_estimators=180, min_samples_leaf=2, random_state=42, n_jobs=-1)),
    ])
    pipeline.fit(X_train, y_train)
    holdout = pipeline.predict(X_test)
    metrics = {
        "mae_lakhs": float(mean_absolute_error(y_test, holdout)),
        "r2": float(r2_score(y_test, holdout)),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }
    pipeline.fit(X, y)
    return pipeline, metrics


def prediction_frame(values):
    return pd.DataFrame([{col: values[col] for col in FEATURES}], columns=FEATURES)


def page_heading(kicker, title, description):
    st.markdown(f'<div class="section-kicker">{kicker}</div><div class="section-title">{title}</div><p class="muted">{description}</p>', unsafe_allow_html=True)


def chart_style(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#34465b", size=12),
        margin=dict(l=16, r=16, t=28, b=16),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#142235", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e4eaf1", zeroline=False)
    fig.update_yaxes(gridcolor="#edf1f5", zeroline=False)
    return fig


try:
    data = load_data()
    data_signature = f"{DATA_PATH.stat().st_mtime_ns}-{len(data)}-{data['price_lakhs'].sum():.2f}"
    model, metrics = train_model(data_signature)
except Exception as exc:
    st.error("The dashboard could not load its data or prepare the model.")
    st.exception(exc)
    st.info("Check that you opened Terminal in the extracted project folder and installed packages with `pip install -r requirements.txt`.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand-mark">⌂</div><div class="brand-name">PropertyLens</div><div class="brand-sub">INDIA REAL ESTATE INTELLIGENCE</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Estimate Price", "Market Insights", "Raw Data & Sources"],
        index=0,
    )
    page_hints = {
        "Overview": "Market snapshot",
        "Estimate Price": "Calculate a property value",
        "Market Insights": "Explore price patterns",
        "Raw Data & Sources": "Inspect and export records",
    }
    st.caption(page_hints[page])
    st.divider()
    st.markdown("**YOUR DATASET**")
    st.write(f"🧾  {len(data):,} demo records")
    st.write(f"📍  {data['city'].nunique()} Indian cities")
    st.write("💰  INR · Lakhs · Crores")
    st.divider()
    st.caption("Demo analytics only. Confirm real market values independently.")

st.markdown(
    '<div class="hero"><div class="hero-pill">PROPERTY ANALYTICS WORKSPACE</div>'
    '<h1>Understand a property’s value.<br>Make a more informed decision.</h1>'
    '<p>Explore city-level trends, compare homes, and estimate a residential property price using location, built-up area, configuration and amenities.</p></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="warning-note">Data transparency: the built-in 1,400-row history is synthetic demo data for learning and testing. Public listing samples are separate asking-price examples—not verified sale transactions.</div>',
    unsafe_allow_html=True,
)
st.write("")

if page == "Overview":
    page_heading("MARKET SNAPSHOT", "India property overview", "A quick look at the bundled demo records. Values below are illustrative, not current market quotations.")
    city_count = data["city"].nunique()
    avg_price = float(data["price_lakhs"].mean())
    median_price = float(data["price_lakhs"].median())
    avg_area = int(data["area_sqft"].mean())
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Demo records", f"{len(data):,}", help="Rows in the bundled synthetic dataset")
    k2.metric("Cities covered", f"{city_count}", help="Indian cities represented in the demo dataset")
    k3.metric("Average demo price", money_lakhs(avg_price), help="Mean of synthetic sample prices")
    k4.metric("Average area", f"{avg_area:,} sq ft")

    st.write("")
    left, right = st.columns([1.15, 0.85], gap="large")
    city_summary = data.groupby("city", as_index=False).agg(avg_price_lakhs=("price_lakhs", "mean"), records=("record_id", "count"))
    city_summary = city_summary.sort_values("avg_price_lakhs", ascending=True)
    with left:
        st.markdown("**Average demo price by city**")
        fig = px.bar(
            city_summary, x="avg_price_lakhs", y="city", orientation="h", text=city_summary["avg_price_lakhs"].map(lambda x: f"₹{x:.0f} L"),
            color="avg_price_lakhs", color_continuous_scale=[[0, "#bce7df"], [1, "#0f766e"]],
            labels={"city": "City", "avg_price_lakhs": "Average price (₹ lakh)"},
            hover_data={"records": True, "avg_price_lakhs": ":.1f"},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Average price (₹ lakh)", yaxis_title="", height=430)
        st.plotly_chart(chart_style(fig, 430), use_container_width=True)
    with right:
        st.markdown("**Illustrative price trend**")
        yearly = data.groupby("sale_year", as_index=False)["price_lakhs"].mean()
        fig2 = px.area(yearly, x="sale_year", y="price_lakhs", markers=True,
                       labels={"sale_year": "Year", "price_lakhs": "Average price (₹ lakh)"})
        fig2.update_traces(line_color="#0f766e", fillcolor="rgba(15,118,110,0.14)", marker_color="#0f766e")
        fig2.update_layout(xaxis_title="Year", yaxis_title="Average price (₹ lakh)", height=430)
        st.plotly_chart(chart_style(fig2, 430), use_container_width=True)
        st.markdown('<div class="note">The trend uses generated teaching data, not a verified house-price index.</div>', unsafe_allow_html=True)

    st.write("")
    page_heading("SAMPLE RECORDS", "Recent demo properties", "A small preview of the data feeding the model.")
    recent = data.sort_values(["sale_year", "price_lakhs"], ascending=[False, False]).head(8).copy()
    recent["Price"] = recent["price_lakhs"].map(money_lakhs)
    recent["Area"] = recent["area_sqft"].map(lambda v: f"{v:,} sq ft")
    st.dataframe(recent[["city", "locality", "property_type", "Area", "bhk", "sale_year", "Price"]].rename(columns={"city":"City", "locality":"Locality", "property_type":"Property type", "bhk":"BHK", "sale_year":"Demo year"}), use_container_width=True, hide_index=True)

elif page == "Estimate Price":
    page_heading("PRICE ESTIMATOR", "Estimate a property value", "Enter property details and select Estimate to calculate an illustrative price in Indian rupees.")
    st.markdown('<div class="note">Tip: choose the closest available locality. This model uses synthetic demo data, so treat the output as a project demonstration—not an official valuation.</div>', unsafe_allow_html=True)
    st.write("")

    # Keep inputs outside a form so changing the city immediately refreshes localities.
    col_a, col_b, col_c = st.columns(3, gap="large")
    cities = sorted(data["city"].unique().tolist())
    with col_a:
        st.markdown("**01 · Location & size**")
        preferred_city = cities.index("Hyderabad") if "Hyderabad" in cities else 0
        city = st.selectbox("City", cities, index=preferred_city, key="estimate_city")
        city_frame = data[data["city"] == city]
        localities = sorted(city_frame["locality"].dropna().astype(str).unique().tolist())
        if not localities:
            localities = ["Unknown"]
        locality = st.selectbox("Locality", localities, key="estimate_locality")
        property_type = st.selectbox("Property type", ["Apartment", "Independent House", "Villa", "Builder Floor"], key="estimate_property_type")
        area = st.number_input("Built-up area (sq ft)", min_value=200, max_value=10000, value=1200, step=50, key="estimate_area")
    with col_b:
        st.markdown("**02 · Configuration**")
        bhk = st.selectbox("Bedrooms (BHK)", [1, 2, 3, 4, 5, 6], index=2, key="estimate_bhk")
        bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4, 5], index=2, key="estimate_bathrooms")
        age = st.slider("Property age (years)", min_value=0, max_value=50, value=5, key="estimate_age")
        furnishing = st.selectbox("Furnishing", ["Unfurnished", "Semi-Furnished", "Furnished"], index=1, key="estimate_furnishing")
    with col_c:
        st.markdown("**03 · Amenities**")
        parking = int(st.checkbox("Car parking", value=True, key="estimate_parking"))
        lift = int(st.checkbox("Lift available", value=True, key="estimate_lift"))
        gated = int(st.checkbox("Gated community", value=True, key="estimate_gated"))
        gym = int(st.checkbox("Gym", value=False, key="estimate_gym"))
        pool = int(st.checkbox("Swimming pool", value=False, key="estimate_pool"))
        st.caption(f"Reference year used by the demo model: {int(data['sale_year'].max())}")

    submitted = st.button("Estimate property price", type="primary", use_container_width=True, key="estimate_submit")

    if submitted:
        row = prediction_frame({
            "city": city, "locality": locality, "property_type": property_type,
            "area_sqft": float(area), "bhk": int(bhk), "bathrooms": int(bathrooms),
            "age_years": int(age), "furnishing_status": furnishing,
            "parking": parking, "lift": lift, "gated_community": gated,
            "gym": gym, "swimming_pool": pool, "sale_year": int(data["sale_year"].max()),
        })
        predicted_lakhs = max(1.0, float(model.predict(row)[0]))
        margin = max(metrics["mae_lakhs"], predicted_lakhs * 0.08)
        low, high = max(0, predicted_lakhs - margin), predicted_lakhs + margin
        st.write("")
        st.markdown(
            f'<div class="estimate-panel"><div class="section-kicker">MODEL ESTIMATE · ILLUSTRATIVE</div>'
            f'<div class="estimate-value">{money_lakhs(predicted_lakhs, compact=False)}</div>'
            f'<div class="muted" style="margin-top:8px">Indicative range: <b>{money_lakhs(low, compact=False)} – {money_lakhs(high, compact=False)}</b></div></div>',
            unsafe_allow_html=True,
        )
        m1, m2, m3 = st.columns(3)
        m1.metric("Approx. price per sq ft", inr_grouping(predicted_lakhs * 100000 / area))
        m2.metric("Holdout model MAE", money_lakhs(metrics["mae_lakhs"]))
        m3.metric("Amenities selected", f"{parking + lift + gated + gym + pool} / 5")
        estimate_csv = row.copy()
        estimate_csv["estimated_price_lakhs"] = round(predicted_lakhs, 2)
        st.download_button(
            "Download estimate as CSV",
            estimate_csv.to_csv(index=False).encode("utf-8"),
            file_name="property_price_estimate.csv",
            mime="text/csv",
            use_container_width=True,
        )

elif page == "Market Insights":
    page_heading("MARKET EXPLORER", "Explore property price patterns", "Filter cities and compare area, configuration and year-wise demo prices.")
    selected_cities = st.multiselect("Cities to compare", sorted(data["city"].unique()), default=sorted(data["city"].unique())[:5])
    insights = data[data["city"].isin(selected_cities)].copy() if selected_cities else data.iloc[0:0].copy()
    if insights.empty:
        st.info("Select at least one city to display charts.")
    else:
        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("**Built-up area vs price**")
            sample = insights.sample(min(800, len(insights)), random_state=42)
            scatter = px.scatter(sample, x="area_sqft", y="price_lakhs", color="city", hover_data=["locality", "bhk", "sale_year"],
                                 labels={"area_sqft":"Built-up area (sq ft)", "price_lakhs":"Price (₹ lakh)"}, opacity=.72)
            scatter.update_layout(xaxis_title="Built-up area (sq ft)", yaxis_title="Demo price (₹ lakh)")
            st.plotly_chart(chart_style(scatter, 400), use_container_width=True)
        with b:
            st.markdown("**Median price by BHK**")
            bhk_summary = insights.groupby(["bhk", "city"], as_index=False)["price_lakhs"].median()
            bars = px.bar(bhk_summary, x="bhk", y="price_lakhs", color="city", barmode="group",
                          labels={"bhk":"Bedrooms (BHK)", "price_lakhs":"Median price (₹ lakh)"})
            bars.update_layout(xaxis_title="Bedrooms (BHK)", yaxis_title="Median demo price (₹ lakh)")
            st.plotly_chart(chart_style(bars, 400), use_container_width=True)
        st.markdown("**Year-wise demo price movement**")
        year_summary = insights.groupby(["sale_year", "city"], as_index=False)["price_lakhs"].median()
        trend = px.line(year_summary, x="sale_year", y="price_lakhs", color="city", markers=True,
                        labels={"sale_year":"Year", "price_lakhs":"Median price (₹ lakh)"})
        trend.update_layout(xaxis_title="Year", yaxis_title="Median demo price (₹ lakh)")
        st.plotly_chart(chart_style(trend, 380), use_container_width=True)
        st.caption("Historical years are synthetic teaching labels; do not interpret these lines as actual market movement.")

else:
    page_heading("DATA & SOURCES", "Raw data explorer", "Inspect the bundled training sample and public listing examples separately.")
    st.markdown('<div class="warning-note">The model dataset is synthetic. The public listings below show asking prices from public sources and are not verified completed-sale records.</div>', unsafe_allow_html=True)
    st.write("")
    f1, f2, f3 = st.columns([1.1, 1, .8])
    with f1:
        city_filter = st.multiselect("Filter cities", sorted(data["city"].unique()), default=sorted(data["city"].unique()))
    with f2:
        year_values = sorted(data["sale_year"].unique())
        year_filter = st.slider("Demo year range", min_value=int(min(year_values)), max_value=int(max(year_values)), value=(int(min(year_values)), int(max(year_values))))
    with f3:
        max_rows = st.selectbox("Rows to display", [100, 250, 500, 1000, "All"], index=1)
    view = data[data["city"].isin(city_filter) & data["sale_year"].between(year_filter[0], year_filter[1])].copy()
    rows_count = len(view) if max_rows == "All" else min(len(view), int(max_rows))
    st.caption(f"Displaying {rows_count:,} of {len(view):,} filtered demo rows")
    st.dataframe(view.head(rows_count), use_container_width=True, hide_index=True)
    st.download_button("Download filtered demo data (CSV)", view.to_csv(index=False).encode("utf-8"), file_name="india_property_filtered.csv", mime="text/csv")

    st.divider()
    st.markdown("**Public listing-data sample**")
    if PUBLIC_PATH.exists():
        public_df = pd.read_csv(PUBLIC_PATH)
        st.dataframe(public_df, use_container_width=True, hide_index=True)
        st.download_button("Download public listing sample (CSV)", public_df.to_csv(index=False).encode("utf-8"), file_name="public_listings_extract.csv", mime="text/csv")
    if SOURCES_PATH.exists():
        st.markdown("**Data source manifest**")
        sources = pd.read_csv(SOURCES_PATH)
        display_cols = [col for col in ["dataset", "city_coverage", "type", "url", "included_locally"] if col in sources.columns]
        st.dataframe(sources[display_cols], use_container_width=True, hide_index=True)
        st.markdown("Sources: [Mumbai CSV](https://github.com/happygoluckycodeeditor/pricepredictionmodel/blob/main/Mumbai.csv) · [Delhi CSV](https://github.com/happygoluckycodeeditor/pricepredictionmodel/blob/main/Delhi.csv) · [Bengaluru listing data](https://github.com/Anamikaa-MK/Bengaluru-House-Price-Analysis/blob/main/Data/Bengaluru_House_RawData.csv)")
        st.code("python3 download_data.py", language="bash")
        st.caption("Run the downloader from the project folder to fetch public CSVs. Internet access is required.")

st.markdown(
    f'<div class="footer">PropertyLens · Python + Streamlit · Random Forest regression · '
    f'Holdout MAE {metrics["mae_lakhs"]:.2f} lakh · R² {metrics["r2"]:.3f}<br>'
    'Model metrics are calculated on synthetic demo data only. Not a professional valuation or financial advice.</div>',
    unsafe_allow_html=True,
)
