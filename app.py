import streamlit as st from PIL import Image, ImageDraw, ImageFont import arabic_reshaper from bidi.algorithm import get_display import textwrap import os

الإعدادات الافتراضية

DEFAULT_WIDTH = 1080 DEFAULT_HEIGHT = 1349 DEFAULT_BG_COLOR = "#fdf8f2"  # خلفية بيج فاتحة DEFAULT_TEXT_COLOR = "#521c1c"  # بني مائل إلى الأحمر DEFAULT_HIGHLIGHT_COLOR = "#155e63"  # أزرق مخضر لكلمة "الْيَقِينِ"

تحميل الخطوط

@st.cache_resource def load_fonts(): fonts = {} try: fonts['body'] = ImageFont.truetype("fonts/Amiri-Regular.ttf", size=48) except: fonts['body'] = ImageFont.load_default() try: fonts['title'] = ImageFont.truetype("fonts/AmiriQuran-Regular.ttf", size=54) except: fonts['title'] = fonts['body'] return fonts

def wrap_text(draw, text, font, max_width): words = text.split() lines = [] line = "" for word in words: test_line = f"{line} {word}".strip() reshaped = arabic_reshaper.reshape(test_line) bidi_text = get_display(reshaped) bbox = draw.textbbox((0, 0), bidi_text, font=font) w = bbox[2] - bbox[0] if w <= max_width: line = test_line else: lines.append(line) line = word lines.append(line) return lines

def generate_image(text, image_width, image_height, bg_color, text_color, highlight_color, align, bg_image=None): # الخلفية if bg_image: img = Image.open(bg_image).resize((image_width, image_height)) else: img = Image.new("RGB", (image_width, image_height), color=bg_color)

draw = ImageDraw.Draw(img)
fonts = load_fonts()

# معالجة النص
lines = text.strip().split("\n")
y = 50
for line in lines:
    is_title = "أَتَعْرِفُ" in line or line.endswith("؟")
    font = fonts['title'] if is_title else fonts['body']
    wrapped = wrap_text(draw, line, font, image_width - 100)

    for wrapped_line in wrapped:
        reshaped = arabic_reshaper.reshape(wrapped_line)
        bidi_line = get_display(reshaped)
        bbox = draw.textbbox((0, 0), bidi_line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if align == "center":
            x = (image_width - w) // 2
        elif align == "right":
            x = image_width - w - 50
        else:
            x = 50

        # تمييز كلمة "الْيَقِينِ" في العنوان فقط
        if is_title and "الْيَقِينِ" in wrapped_line:
            parts = wrapped_line.split("الْيَقِينِ")
            x_cursor = x
            for part in parts[:-1]:
                reshaped_part = get_display(arabic_reshaper.reshape(part))
                draw.text((x_cursor, y), reshaped_part, font=font, fill=text_color)
                part_w = draw.textbbox((0, 0), reshaped_part, font=font)[2]
                x_cursor += part_w
                highlight_word = get_display(arabic_reshaper.reshape("الْيَقِينِ"))
                draw.text((x_cursor, y), highlight_word, font=font, fill=highlight_color)
                x_cursor += draw.textbbox((0, 0), highlight_word, font=font)[2]
            final_part = get_display(arabic_reshaper.reshape(parts[-1]))
            draw.text((x_cursor, y), final_part, font=font, fill=text_color)
        else:
            draw.text((x, y), bidi_line, font=font, fill=text_color)
        y += h + 15
return img

مكونات Streamlit

st.title("مولد صور بالنص العربي المشكّل")

text = st.text_area("أدخل النص:", height=300) col1, col2 = st.columns(2) with col1: width = st.number_input("العرض", min_value=200, max_value=2000, value=DEFAULT_WIDTH) with col2: height = st.number_input("الارتفاع", min_value=200, max_value=2000, value=DEFAULT_HEIGHT)

aspect_ratios = {"1:1": (1, 1), "3:4": (3, 4), "4:5": (4, 5), "9:16": (9, 16)} aspect = st.selectbox("أو اختر نسبة أبعاد:", ["اختر نسبة"] + list(aspect_ratios.keys())) if aspect != "اختر نسبة": w_ratio, h_ratio = aspect_ratios[aspect] width = int(height * (w_ratio / h_ratio))

bg_color = st.color_picker("لون الخلفية", DEFAULT_BG_COLOR) text_color = st.color_picker("لون النص", DEFAULT_TEXT_COLOR) highlight_color = st.color_picker("لون التمييز", DEFAULT_HIGHLIGHT_COLOR) align = st.radio("المحاذاة", ["center", "right", "left"]) bg_img_file = st.file_uploader("ارفع صورة كخلفية (اختياري)", type=["png", "jpg", "jpeg"])

if st.button("توليد الصورة") and text: img = generate_image(text, width, height, bg_color, text_color, highlight_color, align, bg_img_file) st.image(img) img.save("generated_image.png") with open("generated_image.png", "rb") as f: st.download_button("تحميل الصورة", f, file_name="arabic_text_image.png", mime="image/png")

