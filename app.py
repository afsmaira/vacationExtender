import streamlit as st
import streamlit.components.v1 as components
from src.vacationextender.core import VacationExtender

import json
import toml
import base64
import datetime
import holidays as hd

DEBUG = False

supported_data = hd.list_supported_countries()
country_codes = sorted(supported_data.keys())

curr_year = datetime.datetime.now().year
dDay = datetime.timedelta(days=1)
app_name = {'pt': 'Estica Férias',
            'en': 'Vacation Extender'}

# 1. DICTIONARY OF TRANSLATIONS
languages = {
    "🇺🇸 English": {
        "title": f"🌴 {app_name['en']} 🌴",
        "subtitle": "Maximize your time off by linking<br>holidays and weekends smartly",
        "settings": "⚙️ Settings",
        "year": "Year",
        "country": "Country (ISO)",
        "state": "State/Subdivision",
        "vac_days": "Total Vacation Days (Balance)",
        "max_periods": "Max Vacation Periods",
        "advanced": "🛠️ Advanced Parameters",
        "min_break": "Min. total days per period",
        "max_break": "Max. total days per period",
        "min_pto_break": "Min. PTO days per period",
        "max_pto_break": "Max. PTO days per period",
        "min_gap": "Min. days gap between periods",
        "top_n": "Number of suggestions in output",
        "button": "🚀 Optimize My Vacation",
        "loading": "Analyzing calendar and optimizing periods...",
        "success": "Optimization complete!",
        "table_header": "📅 Suggested Vacation Plan",
        "footer": "Made with ❤️ by André de Freitas Smaira",
        "error": "Error processing: ",
        "check_iso": "Please check if the Country ISO code and State are correct.",
        "caption": "Legend: PTO = Vacation days used | TOTAL = Total days off (including holidays and weekends)",
        "add_holidays": "Extra/Local Holidays",
        "mandatory": "Mandatory Work Days",
        "add_date_btn": "Add Date",
        "clear_btn": "Clear",
        "added_dates": "Selected Dates:",
        "holidays_consume": "Holidays consume PTO days?",
        "h_holidays_consume": "If enabled, holidays occurring during your vacation will count towards your used PTO balance.",
        "h_year": "The calendar year for which you want to plan your vacations.",
        "h_country": "Select your country to automatically load national holidays.",
        "h_state": "Select your state/region for local holidays.",
        "h_vac_days": "Total number of PTO (Paid Time Off) days you have available.",
        "h_max_periods": "The maximum number of separate vacation blocks the algorithm should suggest.",
        "h_min_max": "Constraints on the duration (in total days) of each vacation block.",
        "h_pto_min_max": "Constraints on the duration (in PTO days) of each vacation block.",
        "h_top_n": "Number of alternative vacation plans to display.",
        "h_add_hols": "Add holidays that are not in the standard list (e.g., municipal holidays).",
        "h_mandatory": "Days when you MUST work (the algorithm will avoid these days for vacation).",
        "h_min_gap": "Minimum number of days between two vacation periods to ensure they are well distributed throughout the year.",
        "h_config": "Touch button 'Vacation Config' at top to start!",
        "hols_list_title": "📅  Holidays Considered for Calculation",
        "custom_holiday": "User Added",
        "no_hols": "No holidays identified for this selection.",
        "date_format": "%m/%d",
        "date_display": "%b %d",
        "config_btn": "Start Planning",
        "save_btn": "Save",

        "feedback_title": "💡 Suggestions for improvement?",
        "feedback_desc": f"Help us make {app_name['en']} even better!",
        "github_btn": "Report bug on GitHub",
        "forms_btn": "Send feedback (Forms)",
        "forms_url": "https://forms.gle/2ocBymDTqBU4fR3EA",

        "about_title": "🚀 About the Project",
        "about_desc": f"{app_name['en']} is the first of a series of apps designed to simplify your life.",
        "follow_btn": "Follow our journey",
        "follow_url": "https://linktr.ee/afs.life.apps",

        "section_commom_custom": "Commom Custom Holidays",
        "carnival": "Include Carnival (Brazil)?",
        "h_carnival": "Carnival is an optional holiday in most of Brazil. Check this to include it in your vacation planning.",

        "corpus": "Include Corpus Christi (Brazil)?",
        "h_corpus": "Corpus Christi is an optional holiday in most of Brazil. Check this to include it in your vacation planning.",

        "must_be": "Fixed Vacation Dates",
        "h_must_be": "Select days you MUST be off",

        "export": "Settings Export",

        "must_start_on": "Fixed Start Dates",
        "h_must_start_on": "Force vacation periods to start exactly on these dates (e.g., for booked flights). The number of dates cannot exceed the 'Max Vacation Periods'.",

        "must_end_on": "Fixed End Dates",
        "h_must_end_on": "Force vacation periods to end exactly on these dates. The number of dates cannot exceed the 'Max Vacation Periods'.",

        "section_months": "Months",
        "required_months": "Full vacations in:",
        "h_required_months": "The vacation period must start and end entirely within the selected months.",
        "start_months": "Vacations starting in:",
        "h_start_months": "Vacations must begin in these months, but are allowed to end in the next month.",
        "month_names": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                        "October", "November", "December"],
        "chosen": "Chosen",

        "date_input_format": "MM/DD/YYYY",

        "section_rules": "⚙️ Rules & Limits",
        "section_calendar": "📅 Calendar & Constraints",
        "h_section_rules": "Configure duration limits, gaps and balance rules.",
        "h_section_calendar": "Customize holidays, fixed dates and month preferences.",

        "section_terms": "⚖️ Terms & Privacy",
        "terms_file": "TERMS_EN.md"
    },
    "🇧🇷 Português": {
        "title": f"🌴 {app_name['pt']} 🌴",
        "subtitle": "Maximize seu descanso conectando feriados e fins de semana de forma inteligente",
        "settings": "⚙️ Configurações",
        "year": "Ano",
        "country": "País (ISO)",
        "state": "Estado",
        "vac_days": "Total de dias de férias (Saldo)",
        "max_periods": "Máximo de períodos",
        "advanced": "🛠️ Ajustes Avançados",
        "min_break": "Mín. total de dias por período",
        "max_break": "Máx. total de dias por período",
        "min_pto_break": "Mín. dias de férias por período",
        "max_pto_break": "Máx. dias de férias por período",
        "min_gap": "Mín. dias entre períodos",
        "top_n": "Número de sugestões na saída",
        "button": "🚀 Otimizar Minhas Férias",
        "loading": "Analisando o calendário...",
        "success": "Otimização concluída!",
        "table_header": "📅 Sugestão de Férias",
        "footer": "Feito com ❤️ por André de Freitas Smaira",
        "error": "Erro ao processar: ",
        "check_iso": "Verifique se o código do país e estado estão corretos.",
        "caption": "Legenda: PTO = Dias de férias usados | TOTAL = Dias totais de descanso (incluindo feriados e fins de semana)",
        "add_holidays": "Feriados Extras/Locais",
        "mandatory": "Dias de trabalho obrigatórios",
        "add_date_btn": "Adicionar",
        "clear_btn": "Limpar",
        "added_dates": "Datas selecionadas:",
        "holidays_consume": "Feriados consomem dias de férias?",
        "h_holidays_consume": "Se ativado, feriados que caem durante as férias serão contados como dias gastos do seu saldo de férias.",
        "h_year": "O ano do calendário para o qual você deseja planejar suas férias.",
        "h_country": "Selecione seu país para carregar automaticamente os feriados nacionais.",
        "h_state": "Selecione seu estado ou região para feriados locais.",
        "h_vac_days": "Quantidade total de dias de férias que você tem disponível para usar.",
        "h_max_periods": "O número máximo de períodos (blocos) em que suas férias podem ser divididas.",
        "h_min_max": "Limites de duração (em dias totais) para cada período de descanso.",
        "h_pto_min_max": "Limites de duração (em dias de férias) para cada período de descanso.",
        "h_top_n": "Número de diferentes sugestões de planos de férias que você quer ver.",
        "h_add_hols": "Adicione feriados que não estão na lista padrão (ex: feriados municipais).",
        "h_mandatory": "Dias em que você NÃO pode estar de férias (ex: reuniões importantes).",
        "h_min_gap": "Número mínimo de dias entre dois períodos de férias para garantir que fiquem bem distribuídas ao longo do ano.",
        "h_config": "Clique no botão 'Configurar Férias' ali no topo para começar!",
        "hols_list_title": "📅  Feriados Considerados para o Cálculo",
        "custom_holiday": "Adicionado pelo Usuário",
        "no_hols": "Nenhum feriado identificado para esta seleção.",
        "date_format": "%d/%m",
        "date_display": "%d/%m",
        "config_btn": "Começar Planejamento",
        "save_btn": "Salvar",

        "feedback_title": "💡 Sugestões de melhoria?",
        "feedback_desc": f"Ajude-nos a tornar o {app_name['pt']} ainda melhor!",
        "github_btn": "Reportar bug no GitHub",
        "forms_btn": "Dar sugestão (Forms)",
        "forms_url": "https://forms.gle/heFh7g56DH9mjA8s8",

        "about_title": "🚀 Sobre o Projeto",
        "about_desc": f"O {app_name['pt']} é o primeiro de uma série de apps criados para simplificar sua vida.",
        "follow_btn": "Siga nossa jornada nas Redes Sociais",
        "follow_url": "https://linktr.ee/afs.life.apps",

        "section_commom_custom": "Pontos Facultativos Comuns",
        "carnival": "Considerar Carnaval como feriado?",
        "h_carnival": "O Carnaval é ponto facultativo na maior parte do Brasil. Marque para considerá-lo como feriado.",

        "corpus": "Considerar Corpus Christi como feriado?",
        "h_corpus": "O Corpus Christi é ponto facultativo na maior parte do Brasil. Marque para considerá-lo como feriado.",

        "must_be": "Dias de Férias Obrigatórios",
        "h_must_be": "Selecione dias que você quer que necessariamente faça parte das férias.",

        "export": "Exportar Configuração",

        "must_start_on": "Datas de Início Fixas",
        "h_must_start_on": "Obriga os períodos de férias a começar exatamente nestas datas (ex: voos já comprados). O total de datas não pode exceder o Máximo de Períodos.",

        "must_end_on": "Datas de Término Fixas",
        "h_must_end_on": "Obriga os períodos de férias a terminar exatamente nestas datas. O total de datas não pode exceder o Máximo de Períodos.",

        "section_months": "Meses",
        "required_months": "Férias inteiras em:",
        "h_required_months": "O período de férias deve começar e terminar totalmente dentro dos meses selecionados.",
        "start_months": "Férias iniciando em:",
        "h_start_months": "As férias devem começar nestes meses, mas podem terminar no mês seguinte.",
        "month_names": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro",
                        "Outubro", "Novembro", "Dezembro"],
        "chosen": "Escolhidos",

        "date_input_format": "DD/MM/YYYY",

        "section_rules": "⚙️ Regras e Limites",
        "section_calendar": "📅 Calendário e Restrições",

        "h_section_rules": "Configure limites de duração, intervalo entre férias e regras de saldo.",
        "h_section_calendar": "Personalize feriados, datas fixas e preferências de meses.",

        "section_terms": "⚖️ Termos & Privacidade",
        "terms_file": "TERMS_PT.md"
    }
}
lang_to_language = {'pt': "🇧🇷 Português",
                    'br': "🇧🇷 Português",
                    'en': "🇺🇸 English"}

# --- LANGUAGE SELECTOR ---
get_lang = st.query_params.get("lang", "en")
lang_options = list(languages.keys())
selected_lang = st.selectbox(
    "🌐 Language / Idioma", lang_options,
    index=lang_options.index(
        lang_to_language.get(get_lang, "🇺🇸 English")
    )
)
t = languages[selected_lang]

st.set_page_config(
    page_title=app_name['en'],
    page_icon="🌴",
    layout="centered"
)

if 'extra_holidays' not in st.session_state:
    st.session_state.extra_holidays = []
if 'mandatory_days' not in st.session_state:
    st.session_state.mandatory_days = []
if 'must_be_days' not in st.session_state:
    st.session_state.must_be_days = []
if 'must_start_on' not in st.session_state:
    st.session_state.must_start_on = []
if 'must_end_on' not in st.session_state:
    st.session_state.must_end_on = []
if "btn_clicks" not in st.session_state:
    st.session_state.btn_clicks = 0
if "config_ready" not in st.session_state:
    st.session_state.config_ready = False

# Title & Description
col_left, col_center, col_right = st.columns([1, 8, 1])
with col_center:
    st.title(t["title"])
st.markdown(
    f"""<div style='text-align: center; font-size: 24px; font-weight: bold; padding-top: 10px; padding-bottom: 20px;'>
        {t['subtitle']}
    </div>""",
    unsafe_allow_html=True
)

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header(t["settings"])

    year = st.number_input(
        t["year"],
        min_value=curr_year, max_value=curr_year + 10, value=curr_year + 1,
        help=t['h_year']
    )

    col1, col2 = st.columns(2)
    with col1:
        default_country_index = country_codes.index("BR") \
            if "BR" in country_codes else 0
        country = st.selectbox(
            t["country"],
            options=country_codes, index=default_country_index,
            help=t['h_country']
        )
    state_options = sorted(supported_data.get(country, []))
    if state_options:
        with col2:
            subdivision = st.selectbox(
                t["state"], options=state_options,
                help=t['h_state']
            )
    else:
        subdivision = None

    st.divider()

    vac_days = st.number_input(
        t["vac_days"],
        min_value=1, max_value=366, value=30, step=1,
        help=t['h_vac_days']
    )
    max_periods = st.number_input(
        t["max_periods"],
        min_value=1, max_value=vac_days, value=3, step=1,
        help=t['h_max_periods']
    )
    with st.expander(t["section_rules"], expanded=False):
        st.caption(t["h_section_rules"])
        holidays_consume_pto = st.checkbox(
            t["holidays_consume"],
            value=True,
            help=t["h_holidays_consume"]
        )
        min_break = st.number_input(
            t["min_break"],
            min_value=1, max_value=366, value=1, step=1,
            help=t['h_min_max']
        )
        max_break = st.number_input(
            t["max_break"],
            min_value=1, max_value=366, value=366, step=1
        )
        min_pto_break = st.number_input(
            t["min_pto_break"],
            min_value=1, max_value=vac_days, value=1, step=1,
            help=t['h_pto_min_max']
        )
        max_pto_break = st.number_input(
            t["max_pto_break"],
            min_value=1, max_value=vac_days, value=vac_days, step=1
        )
        min_gap = st.number_input(
            t['min_gap'],
            min_value=1, max_value=366, value=60, step=1,
            help=t['h_min_gap']
        )
        top_n = st.number_input(
            t["top_n"],
            min_value=1, max_value=10, value=1, step=1,
            help=t['h_top_n']
        )

        st.markdown(f"**{t['add_holidays']}**",
                    help=t['h_add_hols'])
        col_date, col_btn = st.columns([2, 1])
        new_h = col_date.date_input(
            "Holidays", label_visibility="collapsed", key="in_h",
            min_value=datetime.date(year, 1, 1),
            max_value=datetime.date(year, 12, 31),
            value=datetime.date(year, 1, 1),
            help=t['h_add_hols'],
            format=t["date_input_format"]
        )
        if col_btn.button(t["add_date_btn"], key="btn_h"):
            if new_h not in st.session_state.extra_holidays:
                st.session_state.extra_holidays.append(new_h)

        if st.session_state.extra_holidays:
            lst = ', '.join(
                dt.strftime(t['date_format'])
                for dt in sorted(set(st.session_state.extra_holidays))
            )
            st.write(f"{t['added_dates']} {lst}")
            if st.button(t["clear_btn"], key="clr_h"):
                st.session_state.extra_holidays = []

        st.divider()

        st.markdown(f"**{t['mandatory']}**",
                    help=t['h_mandatory'])
        col_date_m, col_btn_m = st.columns([2, 1])
        new_m = col_date_m.date_input(
            "Mandatory", label_visibility="collapsed", key="in_m",
            min_value=datetime.date(year, 1, 1),
            max_value=datetime.date(year, 12, 31),
            value=datetime.date(year, 1, 1),
            help=t['h_mandatory'],
            format=t["date_input_format"]
        )
        if col_btn_m.button(t["add_date_btn"], key="btn_m"):
            if new_m not in st.session_state.mandatory_days:
                st.session_state.mandatory_days.append(new_m)

        if st.session_state.mandatory_days:
            lst = ', '.join(
                dt.strftime(t['date_format'])
                for dt in sorted(set(st.session_state.mandatory_days))
            )
            st.write(f"{t['added_dates']} {lst}")
            if st.button(t["clear_btn"], key="clr_m"):
                st.session_state.mandatory_days = []

    with st.expander(t["section_calendar"], expanded=False):
        st.caption(t["h_section_calendar"])

        st.markdown(f"**{t['must_be']}**",
                    help=t['h_must_be'])
        col_date_mb, col_btn_mb = st.columns([2, 1])
        new_mb = col_date_mb.date_input(
            "Must be", label_visibility="collapsed", key="in_mb",
            min_value=datetime.date(year, 1, 1),
            max_value=datetime.date(year, 12, 31),
            value=datetime.date(year, 1, 1),
            help=t['h_must_be'],
            format=t["date_input_format"]
        )
        if col_btn_mb.button(t["add_date_btn"], key="btn_mb"):
            if new_mb not in st.session_state.must_be_days:
                st.session_state.must_be_days.append(new_mb)

        if st.session_state.must_be_days:
            lst = ', '.join(
                dt.strftime(t['date_format'])
                for dt in sorted(set(st.session_state.must_be_days))
            )
            st.write(f"{t['must_be']} {lst}")
            if st.button(t["clear_btn"], key="clr_mb"):
                st.session_state.must_be_days = []

        include_carnival = False
        include_corpus = False
        if country == "BR":
            st.subheader(t['section_commom_custom'])
            include_carnival = st.checkbox(
                t["carnival"],
                value=True,
                help=t["h_carnival"]
            )
            include_corpus = st.checkbox(
                t["corpus"],
                value=True,
                help=t["h_corpus"]
            )

        st.markdown(f"**{t['must_start_on']}**",
                    help=t['h_must_start_on'])
        col_date_ms, col_btn_ms = st.columns([2, 1])
        new_ms = col_date_ms.date_input(
            "Must Start On", label_visibility="collapsed", key="in_ms",
            min_value=datetime.date(year, 1, 1),
            max_value=datetime.date(year, 12, 31),
            value=datetime.date(year, 1, 1),
            help=t['h_must_start_on'],
            format=t["date_input_format"]
        )
        if col_btn_ms.button(t["add_date_btn"], key="btn_ms"):
            if new_ms not in st.session_state.must_start_on:
                if len(set(st.session_state.must_start_on)) < max_periods:
                    st.session_state.must_start_on.append(new_ms)

        if st.session_state.must_start_on:
            lst = ', '.join(
                dt.strftime(t['date_format'])
                for dt in sorted(set(st.session_state.must_start_on))
            )
            st.write(f"{t['must_start_on']} {lst} "
                     f"({len(set(st.session_state.must_start_on))}/{max_periods})")
            if st.button(t["clear_btn"], key="clr_ms"):
                st.session_state.must_start_on = []

        st.divider()

        st.markdown(f"**{t['must_end_on']}**",
                    help=t['h_must_end_on'])
        col_date_me, col_btn_me = st.columns([2, 1])
        new_me = col_date_me.date_input(
            "Must End On", label_visibility="collapsed", key="in_me",
            min_value=datetime.date(year, 1, 1),
            max_value=datetime.date(year, 12, 31),
            value=datetime.date(year, 1, 1),
            help=t['h_must_end_on'],
            format=t["date_input_format"]
        )
        if col_btn_me.button(t["add_date_btn"], key="btn_me"):
            if new_me not in st.session_state.must_end_on:
                if len(set(st.session_state.must_end_on)) < max_periods:
                    st.session_state.must_end_on.append(new_me)

        if st.session_state.must_end_on:
            lst = ', '.join(
                dt.strftime(t['date_format'])
                for dt in sorted(set(st.session_state.must_end_on))
            )
            st.write(f"{t['must_end_on']} {lst} "
                     f"({len(set(st.session_state.must_end_on))}/{max_periods})")
            if st.button(t["clear_btn"], key="clr_me"):
                st.session_state.must_end_on = []

        st.subheader(t["section_months"])

        selected_month_names = st.multiselect(
            t["required_months"],
            options=t["month_names"],
            help=t["h_required_months"]
        )
        required_months = [t["month_names"].index(m) + 1
                           for m in selected_month_names][:max_periods]

        if required_months:
            lst = ', '.join(
                t["month_names"][i - 1] for i in required_months
            )
            st.write(f"{t["required_months"]}: {lst} "
                     f"({len(set(required_months))}/{max_periods})")

        start_month_names = st.multiselect(
            t["start_months"],
            options=t["month_names"],
            help=t["h_start_months"]
        )
        start_months = [t["month_names"].index(m) + 1
                        for m in start_month_names][:max_periods]

        if start_months:
            lst = ', '.join(
                t["month_names"][i - 1] for i in start_months
            )
            st.write(f"{t["start_months"]}: {lst} "
                     f"({len(set(start_months))}/{max_periods})")

    if st.button(
            t['save_btn'], use_container_width=True, type="primary"
    ):
        st.session_state.config_ready = True
        st.session_state.btn_clicks += 1
        js_close = f"""
        <script>
            var sideBtn = window.parent.document.querySelector('button[data-testid="stBaseButton-headerNoPadding"]');
            if (sideBtn) {{ sideBtn.click(); }}
        </script>
        <!--{st.session_state.btn_clicks}-->
        """
        components.html(js_close, height=0, width=0)

# --- CORE LOGIC ---
config_payload = {
    "CALENDAR": {"year": year, "weekend": [5, 6]},
    "LOCATION": {"country_code": country, "subdivision_code": subdivision, "include_observed": False},
    "CONSTRAINTS": {
        "vacation_days": vac_days,
        "max_vac_periods": max_periods,
        "in_holiday_as_pto": holidays_consume_pto,
        "min_total_days_off": min_break,
        "max_total_days_off": max_break,
        "min_vac_days_per_break": min_pto_break,
        "max_vac_days_per_break": max_pto_break,
        "min_gap_days": min_gap,
        "top_n_suggestions": top_n,
        "custom_holidays": list(set(st.session_state.extra_holidays)),
        "forced_work": list(set(st.session_state.mandatory_days)),
        "must_be_vacation": list(set(st.session_state.must_be_days)),
        "must_start_on": list(set(st.session_state.must_start_on)),
        "must_end_on": list(set(st.session_state.must_end_on)),
        "required_months": list(set(required_months)),
        "start_months": list(set(start_months)),
    },
    "ALGORITHM": {
        "algorithm_type": "optimal"
    }
}

try:
    base_hols = hd.country_holidays(
        country, subdiv=subdivision, years=year
    )
except:
    base_hols = {}
all_hols_dict = {d: name for d, name in base_hols.items()}

if include_carnival or include_corpus:
    easter = [k for k, v in all_hols_dict.items()
              if v == 'Sexta-feira Santa']
    if len(easter) > 0:
        if include_carnival:
            carnival = easter[0] - 45 * dDay
            all_hols_dict[carnival - dDay] = 'Carnaval'
            all_hols_dict[carnival] = 'Carnaval'
            all_hols_dict[carnival + dDay] = 'Carnaval'
            st.session_state.extra_holidays.extend(
                [carnival - dDay, carnival, carnival + dDay]
            )
        if include_corpus:
            corpus = easter[0] + 62 * dDay
            all_hols_dict[corpus] = 'Corpus Christi'
            all_hols_dict[corpus + dDay] = 'Corpus Christi'
            st.session_state.extra_holidays.extend(
                [corpus, corpus + dDay]
            )
for d in st.session_state.get("extra_holidays", []):
    if d not in all_hols_dict:
        all_hols_dict[d] = t["custom_holiday"]
sorted_dates = list(sorted(set(all_hols_dict.keys())))

if st.button(
        "🚀 " + t['config_btn'], use_container_width=True, type="primary"
):
    st.session_state.btn_clicks += 1
    components.html(
        """
        <script>
            var sidebarButton = window.parent.document.querySelector('button[data-testid="stExpandSidebarButton"]');
            if (sidebarButton) { sidebarButton.click(); }
        </script>
        """ + f"<!--{st.session_state.btn_clicks}-->",
        height=0, width=0
    )

if st.session_state.config_ready:
    b64_json = base64.b64encode(
        json.dumps(config_payload, indent=4, default=str).encode()
    ).decode()
    b64_toml = base64.b64encode(
        toml.dumps(config_payload).encode()
    ).decode()

    st.markdown("📤 " + t['export'] + ": "
                                     f'<a href="data:file/txt;base64,{b64_json}" download="config.json" style="color: #ff4b4b; text-decoration: none; font-weight: bold;">JSON</a> | '
                                     f'<a href="data:file/txt;base64,{b64_toml}" download="config.toml" style="color: #ff4b4b; text-decoration: none; font-weight: bold;">TOML</a>',
                unsafe_allow_html=True)

    with st.expander(t["hols_list_title"] + f' ({year})'):
        if sorted_dates:
            for d in sorted_dates:
                date_str = d.strftime(t['date_format'])
                st.write(f"**{date_str}** - {all_hols_dict[d]}")
        else:
            st.info(t["no_hols"])

    if st.button(t["button"], type="primary", use_container_width=True):
        try:
            with st.spinner(t["loading"]):
                ve = VacationExtender(config_data=config_payload)
                ve.run()

                st.success(t["success"])
                st.markdown(f"### {t['table_header']}")
                if DEBUG:
                    st.code(str(config_payload), language="text")
                st.caption(t["caption"])
                st.code(str(ve), language="text")

        except Exception as e:
            st.error(f"{t['error']} {e}")
            st.info(t["check_iso"])

# --- FOOTER ---


st.divider()

col_github, col_feedback = st.columns([1, 1])

with col_github:
    st.markdown(f"**{t['about_title']}**")
    st.caption(t['about_desc'])
    st.markdown("**Open Source & Library**")
    st.markdown("""
        [![PyPI version](https://badge.fury.io/py/vacation-extender.svg)](https://pypi.org/project/vacation-extender/)
        [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
    """, unsafe_allow_html=True)

with col_feedback:
    st.markdown(t['feedback_title'])
    st.caption(t['feedback_desc'])
    st.link_button(
        t['forms_btn'],
        t['forms_url'],
        icon="📝"
    )
    st.link_button(
        t['github_btn'],
        'https://github.com/afsmaira/vacationExtender/issues',
        icon="📝"
    )

if selected_lang == '🇧🇷 Português' or \
        (st.session_state.config_ready and country == 'BR'):
            
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #888888; font-size: 0.9em; margin-bottom: 10px;'>
            📱 <b>Quer levar esse planejamento no bolso?</b><br>
            App Android chegando em 2026.
        </div>
        """,
        unsafe_allow_html=True
    )
            
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.link_button(
            "📢 Siga nossa trajetória nas redes sociais!", 
            "https://linktr.ee/afs.life.apps", 
            use_container_width=True
        )

st.divider()
st.markdown(
    '''
    <style>
        section[data-testid="stSidebar"] {
            position: fixed;
            top: 0;
            left: 0;
            z-index: 9999;
            height: 100vh;
            box-shadow: 5px 0px 15px rgba(0,0,0,0.1);
        }

        section.main {
            margin-left: 0 !important;
        }
    </style>
    '''
    f"""
    <div style='text-align: center'>
        <p>{t['footer']}</p>
        <a href='https://github.com/afsmaira/vacationExtender'>GitHub Repository</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

with st.expander(t['section_terms'], expanded=False):
    try:
        with open(t['terms_file'], "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.error("Legal docs not found.")
        st.markdown(f"[Ver Termos no GitHub](https://github.com/afsmaira/vacationExtender/blob/main/{t['terms_file']})")
