
import streamlit as st
import os, json
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks.base import BaseCallbackHandler

# ── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🧳 Agentic Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Agentic Travel Planner")
st.caption("Powered by LangChain + MCP  ")
st.divider()

# ── Clé API ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Clé API OpenAI", type="password")
    model   = st.selectbox("Modèle LLM", ["gpt-4o-mini", "gpt-4o"])
    currency = st.selectbox("Devise de conversion", ["USD", "MAD", "EUR", "GBP", "JPY"])
    st.divider()
    st.markdown("**Destinations disponibles :**")
    st.markdown("🇪🇸 Barcelona · 🇫🇷 Paris · 🇲🇦 Marrakech")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# ── Outils (repris du notebook) ───────────────────────────────────────────────
WEATHER_DB = {
    "barcelona": {"avg_temp_c": 22, "condition": "Ensoleillé",         "rain_prob": 10},
    "paris":     {"avg_temp_c": 16, "condition": "Nuageux",            "rain_prob": 35},
    "marrakech": {"avg_temp_c": 28, "condition": "Très ensoleillé",    "rain_prob": 5},
}
DESTINATIONS_DB = {
    "barcelona": {"country": "Espagne",
                  "attractions": ["Sagrada Família", "Parc Güell", "Las Ramblas"],
                  "activities":  ["Visite Gaudí", "Plages", "Boqueria"]},
    "paris":     {"country": "France",
                  "attractions": ["Tour Eiffel", "Louvre", "Montmartre"],
                  "activities":  ["Croisière Seine", "Versailles"]},
    "marrakech": {"country": "Maroc",
                  "attractions": ["Jemaa el-Fna", "Médina", "Jardins Majorelle"],
                  "activities":  ["Excursion Atlas", "Hammam"]},
}
EXCHANGE_RATES = {"USD": 1.0, "EUR": 0.92, "MAD": 10.05, "GBP": 0.79, "JPY": 157.0}

def destination_search(q): 
    d = DESTINATIONS_DB.get(q.strip().lower())
    return json.dumps(d, ensure_ascii=False) if d else f"Non trouvé : {q}"

def budget_calculator(q):
    parts = [p.strip() for p in q.split(",")]
    dest, days = parts[0], int(parts[1])
    c = {"hébergement": 80*days, "alimentation": 40*days,
         "transport": 30*days, "activités": 20*days}
    c["total_USD"] = sum(c.values())
    return json.dumps({"destination": dest, "jours": days, **c}, ensure_ascii=False)

def weather_tool(q):
    d = WEATHER_DB.get(q.strip().lower(), {"avg_temp_c": 20, "condition": "N/A", "rain_prob": 20})
    return json.dumps({"destination": q, **d}, ensure_ascii=False)

def currency_converter(q):
    parts = [p.strip() for p in q.split(",")]
    amount, curr = float(parts[0]), parts[1].upper()
    rate = EXCHANGE_RATES.get(curr, 1.0)
    return json.dumps({"montant_USD": amount, "devise": curr,
                       "résultat": round(amount * rate, 2)}, ensure_ascii=False)

def calculator_tool(expr):
    import re
    if not re.match(r"^[\d\s\+\-\*\/\.\(\)\*\*]+$", expr.strip()): return "Expression invalide"
    return json.dumps({"résultat": round(eval(expr), 4)})

tools = [
    Tool(name="DestinationSearch",  func=destination_search,
         description="Attractions et activités. Input: nom de ville."),
    Tool(name="BudgetCalculator",   func=budget_calculator,
         description="Budget en USD. Input: 'Ville,NbJours'."),
    Tool(name="WeatherTool",        func=weather_tool,
         description="Météo typique. Input: nom de ville."),
    Tool(name="CurrencyConverter",  func=currency_converter,
         description="Conversion USD. Input: 'Montant,DEVISE'."),
    Tool(name="Calculator",         func=calculator_tool,
         description="Calcul arithmétique. Input: expression."),
]

# ── Callback pour journaliser les appels ──────────────────────────────────────
class StreamlitToolLogger(BaseCallbackHandler):
    def __init__(self, log_container):
        self.container = log_container
        self.calls = []
    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "?")
        self.calls.append({"outil": name, "entrée": input_str})
        with self.container:
            st.caption(f"🔧 **{name}** ← `{input_str}`")
    def on_tool_end(self, output, **kwargs):
        preview = str(output)[:80] + ("..." if len(str(output)) > 80 else "")
        if self.calls:
            self.calls[-1]["sortie"] = str(output)
        with self.container:
            st.caption(f"   📤 `{preview}`")

# ── Interface principale ──────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_area(
        "🗺️ Décrivez votre voyage :",
        placeholder="Ex: Planifie un voyage de 5 jours à Barcelona avec budget en MAD",
        height=100
    )

with col2:
    st.markdown("**Options rapides :**")
    if st.button("🇪🇸 5j Barcelona / MAD"):
        query = "Planifie 5 jours à Barcelona avec budget en MAD."
    if st.button("🇫🇷 3j Paris / EUR"):
        query = "Planifie 3 jours à Paris avec budget en EUR."
    if st.button("🇲🇦 4j Marrakech / GBP"):
        query = "Planifie 4 jours à Marrakech avec budget en GBP."

run_btn = st.button("✈️ Planifier mon voyage", type="primary", disabled=not api_key)

if not api_key:
    st.warning("⚠️ Entrez votre clé API OpenAI dans la barre latérale.")

if run_btn and query:
    PROMPT_TPL = """Tu es un assistant de planification de voyages.
Utilise les outils disponibles.
Réponds en français.

Outils: {tools}
Noms: {tool_names}

Question: {input}
{agent_scratchpad}"""
    prompt = PromptTemplate.from_template(PROMPT_TPL)
    llm_inst = ChatOpenAI(model=model, temperature=0.3)
    agent = create_react_agent(llm=llm_inst, tools=tools, prompt=prompt)

    tab1, tab2 = st.tabs(["📋 Plan de voyage", "🔧 Appels d'outils"])

    with tab2:
        st.markdown("**Trace d'exécution en temps réel :**")
        tool_log = st.empty()

    logger = StreamlitToolLogger(tool_log)

    executor = AgentExecutor(
        agent=agent, tools=tools, verbose=False,
        max_iterations=10, handle_parsing_errors=True,
        callbacks=[logger]
    )

    with st.spinner("🤖 L'agent planifie votre voyage..."):
        response = executor.invoke({"input": query})

    with tab1:
        st.success("✅ Plan généré !")
        st.markdown(response["output"])

    with tab2:
        st.divider()
        st.markdown(f"**Total : {len(logger.calls)} appels d'outils**")
        st.dataframe(logger.calls, use_container_width=True)
