import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 1. Konfiguracja strony
st.set_page_config(page_title="Giełda Podręczników", page_icon="📚", layout="centered")

link_do_arkusza = "https://docs.google.com/spreadsheets/d/100a-nStpVPQVFnYPmx463myVn5X34_A2SXwC6VKilr0/edit"

# 2. PANCERNE POŁĄCZENIE Z BAZĄ (Wersja dla Chmury)
@st.cache_resource
def get_google_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

client = get_google_client()
arkusz = client.open_by_url(link_do_arkusza).sheet1

@st.cache_data(ttl=5)
def get_data():
    dane = arkusz.get_all_records()
    return pd.DataFrame(dane)

df = get_data()

# 3. Własny styl CSS (Ten sam, co poprzednio)
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }

    /* --- PUNK 1: Naprawa widoczności formularza --- */
    div[data-testid="stForm"] {
        background-color: #ffffff !important;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        border: 1px solid #f3f4f6;
    }
    /* Napisy nad polami (Imię, Tytuł itd.) - ciemne, duże i pogrubione */
    div[data-testid="stForm"] label p {
        color: #1f2937 !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }
    /* Same pola do wpisywania - jasne tło, ciemny tekst, wyraźne ramki */
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] div[data-baseweb="select"] > div {
        background-color: #f9fafb !important;
        color: #111827 !important;
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    div[data-testid="stSidebar"] label p {
        font-size: 22px !important; /* Duża czcionka klas */
        font-weight: 600 !important;
        padding-bottom: 8px;
    }
    div[data-testid="stSidebar"] h1 {
        font-size: 34px !important; /* Ogromny nagłówek Kategorie */
        font-weight: 800 !important;
    }

    .ogloszenie-card {
        background-color: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03); margin-bottom: 20px;
        border-left: 6px solid #10b981; border-top: 1px solid #f3f4f6;
        border-right: 1px solid #f3f4f6; border-bottom: 1px solid #f3f4f6;
    }
    .tytul-ksiazki { font-size: 20px; font-weight: 800; color: #111827; margin-bottom: 5px; }
    .dane-sprzedawcy { color: #6b7280; font-size: 14px; margin-bottom: 15px; }
    .cena-tag { color: #10b981; font-size: 24px; font-weight: 900; float: right; margin-top: -40px;}
    .ig-btn {
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none;
        font-size: 14px; font-weight: 700; display: inline-block; transition: transform 0.2s;
    }
    .ig-btn:hover { transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# 4. Pasek Boczny - Filtry i Plakat
st.sidebar.title("Kategorie")
wybrana_opcja = st.sidebar.radio(
    "Gdzie idziemy?",
    ("📚 Klasa 1", "📚 Klasa 2", "📚 Klasa 3", "📚 Klasa 4", "➕ Dodaj ogłoszenie")
)

st.sidebar.markdown("---")
st.sidebar.image("plakat.jpg", use_container_width=True)

# 4.5. Przyklejony pasek Koalicji 2000 na dole ekranu
st.markdown("""
<style>
    /* Robimy miejsce na dole strony, żeby pasek nie zasłaniał ostatnich ogłoszeń */
    .block-container {
        padding-bottom: 80px;
    }

    /* Wygląd paska Koalicji 2000 */
    .koalicja-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #1a428a;
        color: #fbbc05;
        text-align: center;
        padding: 15px 0;
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 1px;
        z-index: 1000;
        box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.15);
    }
</style>

<div class="koalicja-footer">
    PROJEKT ZREALIZOWANY PRZEZ KOALICJĘ 2000 🚀 RAZEM TWORZYMY LEPSZĄ SZKOŁĘ!
</div>
""", unsafe_allow_html=True)
st.title("Szkolna Giełda Podręczników 📖")

# 5. Logika - Formularz dodawania
if wybrana_opcja == "➕ Dodaj ogłoszenie":
    st.subheader("Wystaw swoją książkę na sprzedaż")

    with st.form("dodaj_form"):
        imie_nazwisko = st.text_input("Imię i Nazwisko")
        tytul = st.text_input("Dokładny tytuł książki (np. Oblicza Geografii 3 PR)")
        klasa = st.selectbox("Dla której klasy jest to książka?", ["Klasa 1", "Klasa 2", "Klasa 3", "Klasa 4"])
        cena = st.number_input("Cena (zł)", min_value=0, step=1)
        kontakt_ig = st.text_input("Twój Instagram (np. @antek_kowalski)")

        submit = st.form_submit_button("Dodaj ogłoszenie", type="primary")

        if submit:
            if imie_nazwisko and tytul and kontakt_ig:
                # WYSYŁAMY DANE BEZPOŚREDNIO DO GOOGLE
                arkusz.append_row([imie_nazwisko, tytul, klasa, cena, kontakt_ig])

                st.success(f"Sukces! Książka '{tytul}' trafiła do bazy. Możesz przejść do odpowiedniej zakładki.")
                st.cache_data.clear() # Czyścimy pamięć, żeby apka od razu pobrała nową książkę z bazy
            else:
                st.error("Proszę wypełnić wszystkie pola przed wysłaniem!")

# 6. Logika - Wyświetlanie ofert
else:
    wybrana_klasa = wybrana_opcja.replace("📚 ", "")
    st.subheader(f"Oferty dostępne dla: {wybrana_klasa}")

    if not df.empty and "Klasa" in df.columns:
        # 1. Najpierw filtrujemy bazę tylko dla wybranej klasy
        oferty_klasy = df[df["Klasa"] == wybrana_klasa]

        # 2. DODAJEMY WYSZUKIWARKĘ (Pojawi się tylko w zakładkach klas!)
        szukana_fraza = st.text_input("🔍 Szukaj podręcznika (wpisz tytuł, przedmiot lub autora):", "")

        # 3. Jeśli użytkownik coś wpisał, filtrujemy wyniki po tytule
        if szukana_fraza:
            oferty_klasy = oferty_klasy[oferty_klasy['Tytul'].str.contains(szukana_fraza, case=False, na=False)]

        # 4. Wyświetlamy przefiltrowane ogłoszenia
        if  oferty_klasy.empty:
            st.info("Brak ofert spełniających kryteria wyszukiwania.")
        else:
            for index, row in oferty_klasy.iterrows():
                ig_username = str(row['Kontakt']).replace('@', '').strip()

                st.markdown(f"""
                <div class="ogloszenie-card">
                    <div class="tytul-ksiazki">{row['Tytul']}</div>
                    <div class="dane-sprzedawcy">👤 {row['Imie_Nazwisko']} | 🏫 {row['Klasa']}</div>
                    <div class="cena-tag">{row['Cena']} zł</div>
                    <div>
                        <a href="https://instagram.com/{ig_username}" target="_blank" class="ig-btn">Napisz na IG ({row['Kontakt']})</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Baza danych jest pusta. Bądź pierwszy i dodaj ogłoszenie!")