import streamlit as st
from src.vacationextender.core import VacationExtender

import datetime
import holidays as hd

supported_data = hd.list_supported_countries()
country_codes = sorted(supported_data.keys())

curr_year = datetime.datetime.now().year

# 1. DICTIONARY OF TRANSLATIONS
languages = {
    "English": {
        "title": "🌴 Vacation Extender",
        "subtitle": "Maximize your time off by linking holidays and weekends smartly.",
        "settings": "⚙️ Settings",
        "year": "Year",
        "country": "Country (ISO)",
        "state": "State/Subdivision",
        "vac_days": "Total Vacation Days (Balance)",
        "max_periods": "Max Vacation Periods",
        "advanced": "🛠️ Advanced Parameters",
        "min_break": "Min. days per period",
        "max_break": "Max. days per period",
        "min_gap": "Min. days gap between periods",
        "top_n": "Number of suggestions in output",
        "alpha": "Alpha Factor (Duration vs Efficiency)",
        "alpha_help": "0.0 focuses on pure efficiency. 1.0 prioritizes longer breaks.",
        "button": "🚀 Optimize My Vacation",
        "loading": "Analyzing calendar and optimizing periods...",
        "success": "Optimization complete!",
        "table_header": "📅 Suggested Vacation Plan",
        "footer": "Made with ❤️ by André de Freitas Smaira",
        "error": "Error processing: ",
        "check_iso": "Please check if the Country ISO code and State are correct.",
        "caption": "Legend: PTO = Vacation days used | TOTAL = Total days off (including holidays and weekends)",
        "add_holidays_label": "Extra Holidays",
        "mandatory_label": "Work Days (Block)"
    },
    "Português": {
        "title": "🌴 Vacation Extender",
        "subtitle": "Maximize seu descanso conectando feriados e fins de semana de forma inteligente.",
        "settings": "⚙️ Configurações",
        "year": "Ano",
        "country": "País (ISO)",
        "state": "Estado",
        "vac_days": "Total de dias de férias (Saldo)",
        "max_periods": "Máximo de períodos",
        "advanced": "🛠️ Ajustes Avançados",
        "min_break": "Mín. dias por período",
        "max_break": "Máx. dias por período",
        "min_gap": "Mín. dias entre períodos",
        "top_n": "Número de sugestões na saída",
        "alpha": "Fator Alpha (Duração vs Eficiência)",
        "alpha_help": "0.0 foca em eficiência pura. 1.0 prioriza períodos mais longos.",
        "button": "🚀 Otimizar Minhas Férias",
        "loading": "Analisando o calendário...",
        "success": "Otimização concluída!",
        "table_header": "📅 Sugestão de Férias",
        "footer": "Feito com ❤️ por André de Freitas Smaira",
        "error": "Erro ao processar: ",
        "check_iso": "Verifique se o código do país e estado estão corretos.",
        "caption": "Legenda: PTO = Dias de férias usados | TOTAL = Dias totais de descanso (incluindo feriados e fins de semana)",
        "add_holidays_label": "Feriados Extras",
        "mandatory_label": "Dias de trabalho obrigatórios"
    }
}

# Page Config
st.set_page_config(
    page_title="Vacation Extender", page_icon="🌴", layout="centered"
)

if 'extra_holidays' not in st.session_state:
    st.session_state.extra_holidays = []
if 'mandatory_days' not in st.session_state:
    st.session_state.mandatory_days = []

# --- LANGUAGE SELECTOR ---
selected_lang = st.sidebar.selectbox(
    "🌐 Language / Idioma", ["English", "Português"]
)
t = languages[selected_lang]

# Title & Description
st.title(t["title"])
st.subheader(t["subtitle"])

# --- SIDEBAR INPUTS ---
with (st.sidebar):
    st.header(t["settings"])

    year = st.number_input(
        t["year"],
        min_value=curr_year, max_value=curr_year+10, value=curr_year+1
    )

    col1, col2 = st.columns(2)
    with col1:
        default_country_index = country_codes.index("BR")\
                                if "BR" in country_codes else 0
        country = st.selectbox(
            t["country"],
            options=country_codes, index=default_country_index
        )
    state_options = sorted(supported_data.get(country, []))
    if state_options:
        with col2:
            subdivision = st.selectbox(
                t["state"], options=state_options
            )
    else:
        subdivision = None

    st.divider()

    vac_days = st.number_input(
        t["vac_days"],
        min_value=1, max_value=366, value=30, step=1
    )
    max_periods = st.number_input(
        t["max_periods"],
        min_value=1, max_value=vac_days, value=3, step=1
    )

    with st.expander(t["advanced"]):
        min_break = st.number_input(
            t["min_break"],
            min_value=1, max_value=vac_days, value=1, step=1
        )
        max_break = st.number_input(
            t["max_break"],
            min_value=1, max_value=vac_days, value=vac_days, step=1
        )
        min_gap = st.number_input(
            t['min_gap'],
            min_value=1, max_value=366, value=60, step=1
        )
        top_n = st.number_input(
            t["top_n"],
            min_value=1, max_value=10, value=1, step=1
        )
        alpha = st.slider(
            t["alpha"],
            0.0, 10.0, 0.5,
            help=t["alpha_help"]
        )

        st.markdown(f"**{t['add_holidays_label']}**")
        col_date, col_btn = st.columns([2, 1])
        new_h = col_date.date_input("Holidays", label_visibility="collapsed", key="in_h")
        if col_btn.button(t["add_date_btn"], key="btn_h"):
            if new_h not in st.session_state.extra_holidays:
                st.session_state.extra_holidays.append(new_h)

        if st.session_state.extra_holidays:
            st.write(f"{t['added_dates']} {st.session_state.extra_holidays}")
            if st.button(t["clear_btn"], key="clr_h"):
                st.session_state.extra_holidays = []

        st.divider()

        st.markdown(f"**{t['mandatory_label']}**")
        col_date_m, col_btn_m = st.columns([2, 1])
        new_m = col_date_m.date_input("Mandatory", label_visibility="collapsed", key="in_m")
        if col_btn_m.button(t["add_date_btn"], key="btn_m"):
            if new_m not in st.session_state.mandatory_days:
                st.session_state.mandatory_days.append(new_m)

        if st.session_state.mandatory_days:
            st.write(f"{t['added_dates']} {st.session_state.mandatory_days}")
            if st.button(t["clear_btn"], key="clr_m"):
                st.session_state.mandatory_days = []

# --- CORE LOGIC ---
config_payload = {
    "CALENDAR": {"year": year, "weekend": [5, 6]},
    "LOCATION": {"country_code": country, "subdivision_code": subdivision, "include_observed": False},
    "CONSTRAINTS": {
        "vacation_days": vac_days,
        "max_vac_periods": max_periods,
        "min_vac_days_per_break": min_break,
        "max_vac_days_per_break": max_break,
        "min_gap_days": min_gap,
        "top_n_suggestions": top_n,
        "additional_holidays": st.session_state.extra_holidays,
        "mandatory_work_days": st.session_state.mandatory_days
    },
    "ALGORITHM": {
        "algorithm_type": "optimal",
        "duration_weight_factor_alpha": alpha
    }
}

if st.button(t["button"], type="primary", use_container_width=True):
    try:
        with st.spinner(t["loading"]):
            ve = VacationExtender(config_data=config_payload)
            ve.run()

            st.success(t["success"])
            st.markdown(f"### {t['table_header']}")
            st.code(str(ve), language="text")
            st.caption(t["caption"])

    except Exception as e:
        st.error(f"{t['error']} {e}")
        st.info(t["check_iso"])

# --- FOOTER ---
st.divider()
st.markdown(
    f"""
    <div style='text-align: center'>
        <p>{t['footer']}</p>
        <a href='https://github.com/afsmaira/vacationExtender'>GitHub Repository</a>
    </div>
    """,
    unsafe_allow_html=True
)