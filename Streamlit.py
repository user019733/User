# 📊YouTube-аналітика у Streamlit
import streamlit as st
import pandas as pd
import numpy as np

# --- Налаштування сторінки ---
st.set_page_config(page_title="YouTube Analytics", layout="wide")
st.title("📊 YouTube Аналітика каналів (автоматично)")

# --- 1️⃣ Генерація демо-даних автоматично ---
np.random.seed(1)
n = 200
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

# --- 2️⃣ Обробка даних ---
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["day_of_week"] = df["date"].dt.day_name()
df["hour"] = df["date"].dt.hour

# --- 3️⃣ Автоматичний фільтр (усі дані) ---
filtered = df.copy()
filtered["engagement_rate"] = ((filtered["likes"] + filtered["comments"]) /
                               filtered["views"].replace(0, np.nan)) * 100

# --- 4️⃣ Метрики ---
avg_eng = filtered["engagement_rate"].mean()
total_views = filtered["views"].sum()
total_likes = filtered["likes"].sum()
total_comments = filtered["comments"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📺 Відео", len(filtered))
col2.metric("👀 Перегляди", f"{total_views:,}")
col3.metric("👍 Лайки", f"{total_likes:,}")
col4.metric("💬 Коментарі", f"{total_comments:,}")
st.metric("📈 Середній engagement rate", f"{avg_eng:.2f}%")

# --- 5️⃣ "Heatmap" активності (імітація кольорами) ---
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

# --- 6️⃣ Топ-10 відео ---
st.subheader("🏆 Топ-10 відео за engagement rate")
top10 = filtered.sort_values("engagement_rate", ascending=False).head(10)
st.dataframe(top10[["title", "views", "likes", "comments", "engagement_rate"]])

# --- 7️⃣ Автоматичне збереження ---
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("💾 Завантажити результати (CSV)", csv, "youtube_analysis.csv", "text/csv")

st.success("✅ Автоматичний аналіз завершено — усе готово!")
