import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import io
import requests
import json
from prophet import Prophet
import uuid
import random

# إعداد الصفحة
st.set_page_config(
    page_title="DreamForge™ - Forge Your Dreams",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مستقبلي مستوحى من الفضاء
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    * {font-family: 'Space Mono', monospace;}
    .main {background: linear-gradient(135deg, #1A0033, #330066); color: #E0CCFF; padding: 40px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAIAAAAmkwkpAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAPUlEQVR4nGP4//8/AymG/////z8jIyMjk5OT/////z/Dw8P//////z8/P////z8/P////z8/P////z8DAwMArCkG/9nQ3gAAAABJRU5ErkJggg==');}
    h1, h2, h3 {background: linear-gradient(90deg, #FF33CC, #66FFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; letter-spacing: -1px; text-shadow: 0 2px 15px rgba(255,51,204,0.6);}
    .stButton>button {background: linear-gradient(90deg, #FF33CC, #66FFFF); color: #FFFFFF; border-radius: 50px; font-weight: 700; padding: 15px 35px; font-size: 18px; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); border: none; box-shadow: 0 8px 20px rgba(255,51,204,0.5); text-transform: uppercase;}
    .stButton>button:hover {transform: translateY(-5px) scale(1.05); box-shadow: 0 12px 30px rgba(102,255,255,0.7);}
    .stTextInput>div>div>input {background: rgba(255,255,255,0.1); border: 2px solid #FF33CC; border-radius: 15px; color: #66FFFF; font-weight: bold; padding: 15px; font-size: 18px; box-shadow: 0 5px 15px rgba(255,51,204,0.3); transition: all 0.3s ease;}
    .stTextInput>div>div>input:focus {border-color: #66FFFF; box-shadow: 0 5px 20px rgba(102,255,255,0.5);}
    .stSelectbox>label, .stRadio>label {color: #66FFFF; font-size: 22px; font-weight: 700; text-shadow: 1px 1px 5px rgba(0,0,0,0.5);}
    .stSelectbox>div>div>button {background: rgba(255,255,255,0.1); border: 2px solid #FF33CC; border-radius: 15px; color: #E0CCFF; padding: 15px; font-size: 18px;}
    .stRadio>div {background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.5);}
    .stMarkdown {color: #C4B5FD; font-size: 18px; line-height: 1.6;}
    .share-btn {background: linear-gradient(90deg, #9333EA, #D8B4FE); color: #FFFFFF; border-radius: 50px; padding: 12px 25px; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(147,51,234,0.4); font-size: 16px;}
    .share-btn:hover {transform: translateY(-3px); box-shadow: 0 10px 25px rgba(216,180,254,0.6);}
    .animate-in {animation: fadeInUp 1s forwards; opacity: 0;}
    @keyframes fadeInUp {from {opacity: 0; transform: translateY(20px);} to {opacity: 1; transform: translateY(0);}}
    </style>
""", unsafe_allow_html=True)

# تعريف الحالة الافتراضية
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "payment_verified" not in st.session_state:
    st.session_state["payment_verified"] = False
if "payment_initiated" not in st.session_state:
    st.session_state["payment_initiated"] = False
if "dream_data" not in st.session_state:
    st.session_state["dream_data"] = None

# بيانات PayPal Sandbox
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"

# العنوان والترحيب
st.markdown("""
    <h1 style='font-size: 60px; text-align: center; animation: fadeInUp 1s forwards;'>DreamForge™</h1>
    <p style='font-size: 24px; text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.2s;'>
        Forge Your Dreams into Reality!<br>
        <em>By Anas Hani Zewail • Contact: +201024743503</em>
    </p>
""", unsafe_allow_html=True)

# واجهة المستخدم
st.markdown("<h2 style='text-align: center;'>Weave Your Dream</h2>", unsafe_allow_html=True)
dream_idea = st.text_input("Enter Your Dream (e.g., I want to travel to space):", "I want to travel to space", help="What’s your wildest dream?")
language = st.selectbox("Select Language:", ["English", "Arabic"])
st.session_state["language"] = language
plan = st.radio("Choose Your Dream Plan:", ["Dream Glimpse (Free)", "Dream Spark ($5)", "Dream Crafter ($10)", "Dream Visionary ($20)", "Dream Master ($35/month)"])
st.markdown("""
    <p style='text-align: center;'>
        <strong>Dream Glimpse (Free):</strong> Quick Dream Peek<br>
        <strong>Dream Spark ($5):</strong> Dream Story + Basic Report<br>
        <strong>Dream Crafter ($10):</strong> Dream Path + Full Report<br>
        <strong>Dream Visionary ($20):</strong> Dream Timeline + Tips<br>
        <strong>Dream Master ($35/month):</strong> Daily Updates + Galaxy Access
    </p>
""", unsafe_allow_html=True)

# دوال PayPal
def get_paypal_access_token():
    try:
        url = f"{PAYPAL_API}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Failed to connect to PayPal: {e}")
        return None

def create_payment(access_token, amount, description):
    try:
        url = f"{PAYPAL_API}/v1/payments/payment"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        payment_data = {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{"amount": {"total": amount, "currency": "USD"}, "description": description}],
            "redirect_urls": {
                "return_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?success=true",
                "cancel_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?cancel=true"
            }
        }
        response = requests.post(url, headers=headers, json=payment_data)
        response.raise_for_status()
        for link in response.json()["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
        st.error("Failed to extract payment URL.")
        return None
    except Exception as e:
        st.error(f"Failed to create payment request: {e}")
        return None

# دوال التحليل
def generate_dream_story(dream_idea, language):
    try:
        steps = ["Start", "Challenge", "Victory"]
        values = [20, 10, 80]
        plt.figure(figsize=(8, 6))
        plt.plot(steps, values, marker='o', color="#66FFFF", linewidth=2.5, markersize=12)
        plt.title(f"{dream_idea} Dream Journey" if language == "English" else f"رحلة حلم {dream_idea}", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#1A0033')
        plt.gcf().set_facecolor('#1A0033')
        plt.xticks(color="white", fontsize=12)
        plt.yticks(color="white", fontsize=12)
        plt.grid(True, color="#FF33CC", alpha=0.3)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    except Exception as e:
        st.error(f"Failed to generate dream story: {e}")
        return None

def generate_dream_forecast(dream_idea, language):
    try:
        days = pd.date_range(start="2025-03-03", periods=7).strftime('%Y-%m-%d').tolist()
        progress = [random.randint(20, 100) for _ in range(7)]
        df = pd.DataFrame({'ds': days, 'y': progress})
        df['ds'] = pd.to_datetime(df['ds'])
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        plt.figure(figsize=(10, 6))
        plt.plot(df['ds'], df['y'], label="Dream Progress" if language == "English" else "تقدم الحلم", color="#FF33CC", linewidth=2.5)
        plt.plot(forecast['ds'], forecast['yhat'], label="Forecast" if language == "English" else "التوقعات", color="#66FFFF", linewidth=2.5)
        plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color="#66FFFF", alpha=0.3)
        plt.title(f"{dream_idea} 7-Day Dream Forecast" if language == "English" else f"توقعات حلم {dream_idea} لـ 7 أيام", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#1A0033')
        plt.gcf().set_facecolor('#1A0033')
        plt.legend(fontsize=12, facecolor="#1A0033", edgecolor="white", labelcolor="white")
        plt.xticks(color="white", fontsize=10)
        plt.yticks(color="white", fontsize=10)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        return img_buffer, "Dream on track! Aim for the stars."
    except Exception as e:
        st.error(f"Failed to generate forecast: {e}")
        return None, None

def generate_report(dream_idea, language, dream_story_buffer, forecast_buffer=None, plan="Dream Spark"):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 12
        style.textColor = colors.black
        style.fontName = "Helvetica"

        report = f"DreamForge Report: {dream_idea}\n"
        report += "=" * 50 + "\n"
        report += f"Plan: {plan}\n"
        report += "Your Dream Story Begins Here!\n" if language == "English" else "قصة حلمك تبدأ هنا!\n"
        if language == "Arabic":
            report = arabic_reshaper.reshape(report)
            report = get_display(report)

        content = [Paragraph(report, style)]
        content.append(Image(dream_story_buffer, width=400, height=300))
        
        if forecast_buffer and plan in ["Dream Crafter ($10)", "Dream Visionary ($20)", "Dream Master ($35/month)"]:
            content.append(Image(forecast_buffer, width=400, height=300))
            content.append(Spacer(1, 20))
        
        if plan in ["Dream Visionary ($20)", "Dream Master ($35/month)"]:
            content.append(Paragraph("Dream Tip: Start small - take one step this week!", style))
        
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Failed to generate report: {e}")
        return None

# تشغيل التطبيق
if st.button("Forge My Dream!", key="forge_dream"):
    with st.spinner("Forging Your Dream..."):
        dream_story_buffer = generate_dream_story(dream_idea, language)
        if dream_story_buffer:
            st.session_state["dream_data"] = {"dream_story": dream_story_buffer.getvalue()}
            st.image(dream_story_buffer, caption="Your Dream Journey")
            
            share_url = "https://dreamforge.streamlit.app/"  # استبدل بـ رابطك الفعلي بعد النشر
            telegram_group = "https://t.me/+K7W_PUVdbGk4MDRk"
            
            st.markdown("<h3 style='text-align: center;'>Share Your Dream!</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<a href="https://api.whatsapp.com/send?text=Check%20my%20dream%20on%20DreamForge:%20{share_url}" target="_blank" class="share-btn">WhatsApp</a>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<a href="https://t.me/share/url?url={share_url}&text=DreamForge%20is%20stellar!" target="_blank" class="share-btn">Telegram</a>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" class="share-btn">Messenger</a>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<a href="https://discord.com/channels/@me?message=Explore%20DreamForge:%20{share_url}" target="_blank" class="share-btn">Discord</a>', unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align: center;'>Join our Telegram: <a href='{telegram_group}' target='_blank'>Click Here</a> - Share with 5 friends for a FREE report!</p>", unsafe_allow_html=True)
            
            if plan == "Dream Glimpse (Free)":
                st.info("Unlock your full dream forge with a paid plan!")
            else:
                if not st.session_state["payment_verified"] and not st.session_state["payment_initiated"]:
                    access_token = get_paypal_access_token()
                    if access_token:
                        amount = {"Dream Spark ($5)": "5.00", "Dream Crafter ($10)": "10.00", "Dream Visionary ($20)": "20.00", "Dream Master ($35/month)": "35.00"}[plan]
                        approval_url = create_payment(access_token, amount, f"DreamForge {plan}")
                        if approval_url:
                            st.session_state["payment_url"] = approval_url
                            st.session_state["payment_initiated"] = True
                            unique_id = uuid.uuid4()
                            st.markdown(f"""
                                <a href="{approval_url}" target="_blank" id="paypal_auto_link_{unique_id}" style="display:none;">PayPal</a>
                                <script>
                                    setTimeout(function() {{
                                        document.getElementById("paypal_auto_link_{unique_id}").click();
                                    }}, 100);
                                </script>
                            """, unsafe_allow_html=True)
                            st.info(f"Dream payment opened for {plan}. Complete it to forge your future!")
                elif st.session_state["payment_verified"]:
                    forecast_buffer, reco = generate_dream_forecast(dream_idea, language) if plan in ["Dream Crafter ($10)", "Dream Visionary ($20)", "Dream Master ($35/month)"] else (None, None)
                    if forecast_buffer:
                        st.session_state["dream_data"]["forecast_buffer"] = forecast_buffer.getvalue()
                        st.image(forecast_buffer, caption="7-Day Dream Forecast")
                        st.write(reco)
                    
                    dream_story_buffer = io.BytesIO(st.session_state["dream_data"]["dream_story"])
                    forecast_buffer = io.BytesIO(st.session_state["dream_data"]["forecast_buffer"]) if "forecast_buffer" in st.session_state["dream_data"] else None
                    pdf_data = generate_report(dream_idea, language, dream_story_buffer, forecast_buffer, plan)
                    if pdf_data:
                        st.download_button(
                            label=f"Download Your {plan.split(' (')[0]} Dream Report",
                            data=pdf_data,
                            file_name=f"{dream_idea}_dreamforge_report.pdf",
                            mime="application/pdf",
                            key="download_report"
                        )
                        st.success(f"{plan.split(' (')[0]} Dream Forged! Share to inspire the galaxy!")
