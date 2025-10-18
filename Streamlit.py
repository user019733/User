# 📊 YouTube-аналітика у Streamlit (без seaborn, matplotlib, datetime)
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="YouTube Analytics", layout="wide")
st.title("📊 YouTube Аналітика каналів")

# === 1️⃣ Завантаження CSV або демо ===
uploaded = st.file_uploader("Завантаж CSV (title, views, comments, likes, date, content_type)", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.success("✅ Дані завантажено!")
else:
    st.info("⚙️ Дані не завантажено — створюю демо-набір...")
    np.random.seed(1)
    n = 200
    # створимо дати як рядки (без datetime)
    days = np.random.choice(pd.date_range("2025-01-01", "2025-10-01").astype(str), n)
    hours = np.random.randint(0, 24, n)
    df = pd.DataFrame({
        "title": [f"Video {i+1}" for i in range(n)],
        "views": np.random.randint(100, 20000, n),
        "comments": np.random.randint(0, 500, n),
        "likes": np.random.randint(0, 3000, n),
        "date": [f"{d} {h:02d}:00:00" for d, h in zip(days, hours)],
        "content_type": np.random.choice(["Shorts", "Long-form", "Stream"], n)
    })

# === 2️⃣ Обробка даних ===
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["day_of_week"] = df["date"].dt.day_name()
df["hour"] = df["date"].dt.hour

# === 3️⃣ Фільтри ===
col1, col2, col3 = st.columns(3)
with col1:
    min_date, max_date = df["date"].min(), df["date"].max()
    start_date = st.date_input("Початкова дата", min_date)
with col2:
    end_date = st.date_input("Кінцева дата", max_date)
with col3:
    content_filter = st.selectbox("Тип контенту", ["Усі"] + sorted(df["content_type"].unique()))

filtered = df[
    (df["date"] >= pd.to_datetime(start_date))
    & (df["date"] <= pd.to_datetime(end_date))
]
if content_filter != "Усі":
    filtered = filtered[filtered["content_type"] == content_filter]

# === 4️⃣ Engagement rate ===
filtered["engagement_rate"] = ((filtered["likes"] + filtered["comments"]) / filtered["views"].replace(0, np.nan)) * 100
st.metric("📈 Середній engagement rate", f"{filtered['engagement_rate'].mean():.2f}%")
st.write(f"Відео у вибірці: **{len(filtered)}**")

# === 5️⃣ Heatmap активності (таблично) ===
st.subheader("🔥 Heatmap активності (середні перегляди)")
pivot = filtered.groupby(["day_of_week", "hour"])["views"].mean().unstack(fill_value=0)
pivot = pivot.reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
st.dataframe(pivot.style.background_gradient(cmap="YlOrRd"))

# === 6️⃣ Топ-10 відео за engagement rate ===
st.subheader("🏆 Топ-10 відео за engagement rate")
top10 = filtered.sort_values("engagement_rate", ascending=False).head(10)
st.dataframe(top10[["title","views","likes","comments","engagement_rate"]])

# === 7️⃣ Завантаження результатів ===
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("💾 Завантажити результати (CSV)", csv, "youtube_analysis.csv", "text/csv")

st.success("✅ Аналіз завершено!")
