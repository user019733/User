# 📊 YouTube-аналітика у Streamlit (автоматичне завантаження демо-даних)
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="YouTube Analytics", layout="wide")
st.title("📊 YouTube Аналітика каналів")

# === 1️⃣ Завантаження CSV або автогенерація демо ===
uploaded = st.file_uploader("🔽 Завантаж CSV (title, views, comments, likes, date, content_type)", type=["csv"])

# Якщо CSV не завантажено — створюємо демо-дані
np.random.seed(1)
n = 200
days = np.random.choice(pd.date_range("2025-01-01", "2025-10-01").astype(str), n)
hours = np.random.randint(0, 24, n)
demo_df = pd.DataFrame({
    "title": [f"Video {i+1}" for i in range(n)],
    "views": np.random.randint(100, 20000, n),
    "comments": np.random.randint(0, 500, n),
    "likes": np.random.randint(0, 3000, n),
    "date": [f"{d} {h:02d}:00:00" for d, h in zip(days, hours)],
    "content_type": np.random.choice(["Shorts", "Long-form", "Stream"], n)
})

df = pd.read_csv(uploaded) if uploaded else demo_df
if not uploaded:
    st.info("⚙️ Використовуються демо-дані (можна завантажити свій CSV у верхньому полі).")
else:
    st.success("✅ Дані завантажено!")

# === 2️⃣ Обробка ===
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
avg_eng = filtered["engagement_rate"].mean()

st.metric("📈 Середній engagement rate", f"{avg_eng:.2f}%")
st.write(f"Відео у вибірці: **{len(filtered)}**")

# === 5️⃣ Імітація heatmap через кольори таблиці ===
st.subheader("🔥 Активність переглядів (середні перегляди за день/годину)")

pivot = filtered.groupby(["day_of_week", "hour"])["views"].mean().unstack(fill_value=0)
pivot = pivot.reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])

max_val = pivot.values.max()
def color_intensity(val):
    if max_val == 0:
        return ""
    intensity = int((val / max_val) * 255)
    color = f"background-color: rgba(255, {255-intensity}, {200-intensity//2}, 0.6);"
    return color

st.dataframe(pivot.style.applymap(color_intensity))

# === 6️⃣ Топ-10 за engagement ===
st.subheader("🏆 Топ-10 відео за engagement rate")
top10 = filtered.sort_values("engagement_rate", ascending=False).head(10)
st.dataframe(top10[["title","views","likes","comments","engagement_rate"]])

# === 7️⃣ Завантаження результатів ===
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("💾 Завантажити результати (CSV)", csv, "youtube_analysis.csv", "text/csv")

st.success("✅ Аналіз завершено!")
