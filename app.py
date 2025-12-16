import streamlit as st
import json
import re
from datetime import datetime
from PIL import Image
import easyocr
import tempfile

# ===========================
# إعداد قاعدة البيانات التجريبية
# ===========================
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
except FileNotFoundError:
    db = {"cards": []}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ===========================
# استخراج الرقم القومي
# ===========================
def extract_national_id(text):
    matches = re.findall(r"[23]\d{13}", text)
    return matches[0] if matches else None

# ===========================
# تسجيل البطاقة
# ===========================
def register_card(image):
    reader = easyocr.Reader(['ar'])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image.save(tmp.name)
        result = reader.readtext(tmp.name)
    
    text = " ".join([res[1] for res in result])
    national_id = extract_national_id(text)
    
    if not national_id:
        return "❌ لم يتم العثور على رقم قومي صحيح"
    
    # التحقق من التكرار
    for card in db["cards"]:
        if card["national_id"] == national_id:
            return f"❌ البطاقة مسجلة من قبل عند هذا الفرع"
    
    if len(db["cards"]) >= 6:
        return "⚠️ تم الوصول لعدد البطاقات التجريبي (6 بطاقات)"
    
    db["cards"].append({
        "national_id": national_id,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    return "✅ تم تسجيل البطاقة بنجاح"

# ===========================
# واجهة التطبيق
# ===========================
st.set_page_config(page_title="نظام تسجيل البطاقات", page_icon="📝")

st.title("📝 نظام تسجيل البطاقات التجريبي")
st.markdown("التجربة: فرع واحد، 6 بطاقات فقط")

uploaded_file = st.file_uploader("📷 التقط صورة البطاقة أو ارفعها", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="صورة البطاقة", use_column_width=True)
    if st.button("تسجيل البطاقة"):
        message = register_card(image)
        st.success(message)
