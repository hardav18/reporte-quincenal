import streamlit as st
import requests
import json
from datetime import datetime, date
import plotly.graph_objects as go

# ─────────────────────────────────────────────
#  CONFIGURACION DE PAGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Nequi — Transaccionalidad",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  ESTILOS CORPORATIVOS NEQUI
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');

  html, body, [class*="css"] {
    background-color: #200020 !important;
    color: #ffffff !important;
    font-family: Calibri, 'Nunito', Arial, sans-serif !important;
  }
  .stApp { background-color: #200020 !important; }

  /* Botones */
  .stButton > button {
    background-color: #FF00AA !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 900 !important;
    font-family: Calibri, Arial, sans-serif !important;
    letter-spacing: 0.4px;
  }
  .stButton > button:hover { background-color: #CC0088 !important; }

  /* Inputs */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    background-color: #300030 !important;
    color: white !important;
    border: 1px solid #FF00AA !important;
    border-radius: 4px !important;
    font-family: Calibri, Arial, sans-serif !important;
  }
  .stDateInput > div > div > input {
    background-color: #300030 !important;
    color: white !important;
    border: 1px solid #FF00AA !important;
  }

  /* Labels */
  .stTextInput label, .stNumberInput label,
  .stSelectbox label, .stDateInput label {
    color: #FF00AA !important;
    font-weight: 900 !important;
    font-size: 12px !important;
    letter-spacing: 0.4px;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background-color: #200020 !important;
    border-bottom: 2px solid #FF00AA !important;
    gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    background-color: #200020 !important;
    color: #886688 !important;
    font-weight: 900 !important;
    font-size: 12px !important;
    border-radius: 4px 4px 0 0 !important;
    padding: 8px 20px !important;
  }
  .stTabs [aria-selected="true"] {
    background-color: #2a002a !important;
    color: #FF00AA !important;
    border-bottom: 2px solid #FF00AA !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #1a001a !important;
    border-right: 1px solid #500050 !important;
  }

  /* Métricas */
  [data-testid="metric-container"] {
    background-color: #2a002a !important;
    border: 1px solid #500050 !important;
    border-radius: 6px !important;
    padding: 12px !important;
  }
  [data-testid="metric-container"] label {
    color: #FF00AA !important;
    font-size: 11px !important;
    font-weight: 900 !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 20px !important;
    font-weight: 700 !important;
  }
  [data-testid="stMetricDelta"] { font-size: 12px !important; }

  /* Divider */
  hr { border-color: #500050 !important; }

  /* Success / Error */
  .stSuccess { background-color: #003300 !important; border-color: #00AA44 !important; }
  .stError   { background-color: #330000 !important; border-color: #CC2222 !important; }
  .stWarning { background-color: #332200 !important; border-color: #FF8800 !important; }
  .stInfo    { background-color: #1a002a !important; border-color: #FF00AA !important; }

  /* Texto general */
  p, li, span { color: #ffffff !important; }
  h1, h2, h3 { color: #FF00AA !important; font-weight: 900 !important; }

  /* Selectbox dropdown */
  [data-baseweb="select"] { background-color: #300030 !important; }
  [data-baseweb="menu"]   { background-color: #300030 !important; }

  /* Textarea */
  .stTextArea textarea {
    background-color: #300030 !important;
    color: white !important;
    border: 1px solid #500050 !important;
  }

  /* Tabla nequi */
  .nequi-table {
    width: 100%;
    border-collapse: collapse;
    background: #200020;
    border: 2px solid #ffffff;
    font-family: Calibri, Arial, sans-serif;
  }
  .nequi-table th {
    background: #2a002a;
    color: #ffffff;
    font-size: 13px;
    font-weight: 900;
    padding: 9px 14px;
    border: 1px solid #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }
  .nequi-table td {
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    padding: 9px 14px;
    border: 1px solid #ffffff;
  }
  .nequi-table td.valor { text-align: right; font-size: 14px; }
  .nequi-header-row {
    background: #200020;
    border: 2px solid #ffffff;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
  }
  .nequi-title-pink {
    color: #FF00AA;
    text-align: center;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.4px;
    padding: 7px;
    border: 1px solid #ffffff;
    border-top: none;
    background: #200020;
  }
  .logo-nequi {
    font-size: 26px;
    font-weight: 900;
    color: #ffffff;
    font-family: Calibri, Arial, sans-serif;
    display: inline-block;
  }
  .logo-dot {
    display: inline-block;
    width: 9px; height: 9px;
    background: #FF3355;
    border-radius: 50%;
    margin-right: 2px;
    margin-bottom: 12px;
    vertical-align: top;
  }
  .badge-up   { background:#00AA44; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:900; }
  .badge-down { background:#CC2222; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:900; }
  .badge-eq   { background:#555555; color:#fff; padding:2px 8px; border-radius:3px; font-size:11px; font-weight:900; }
  .banner-comp {
    background: #2a002a;
    border: 1px solid #FF00AA;
    border-radius: 4px;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.7;
  }
  .banner-envio {
    background: #1a001a;
    border: 1px solid #500050;
    border-radius: 6px;
    padding: 14px 16px;
    margin-top: 10px;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONFIGURACION (desde st.secrets)
# ─────────────────────────────────────────────
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

FRANJAS_HISTORICO = ["08:00", "16:00", "20:00"]
FRANJAS_ACTUAL    = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]

# ─────────────────────────────────────────────
#  SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def guardar_historico(franja, fecha_reporte, reg, cli):
    sb = get_supabase()
    sb.table("historico").insert({
        "franja": franja,
        "fecha_reporte": fecha_reporte,
        "registro_transacciones": reg,
        "transacciones_clientes": cli
    }).execute()


def obtener_historico(franja):
    sb = get_supabase()
    r = sb.table("historico").select("*").eq("franja", franja).order("id", desc=True).limit(1).execute()
    return r.data[0] if r.data else None


def guardar_actual(franja, reg, cli):
    hoy = date.today().isoformat()
    sb = get_supabase()
    existe = sb.table("registro_actual").select("id").eq("franja", franja).eq("fecha", hoy).execute()
    data = {"franja": franja, "fecha": hoy, "registro_transacciones": reg, "transacciones_clientes": cli}
    if existe.data:
        sb.table("registro_actual").update(data).eq("franja", franja).eq("fecha", hoy).execute()
    else:
        sb.table("registro_actual").insert(data).execute()


def obtener_actual(franja):
    hoy = date.today().isoformat()
    sb = get_supabase()
    r = sb.table("registro_actual").select("*").eq("franja", franja).eq("fecha", hoy).execute()
    return r.data[0] if r.data else None


def obtener_todos_actual():
    hoy = date.today().isoformat()
    sb = get_supabase()
    r = sb.table("registro_actual").select("*").eq("fecha", hoy).order("franja").execute()
    return r.data or []


def registrar_envio(franja, estado, respuesta):
    try:
        sb = get_supabase()
        sb.table("log_envios").insert({
            "franja": franja, "fecha": date.today().isoformat(),
            "estado": estado, "respuesta": respuesta[:200]
        }).execute()
    except Exception:
        pass


def franja_sup(franja):
    h = int(franja.split(":")[0])
    return "08:00" if h < 16 else "16:00" if h < 20 else "20:00"


# ─────────────────────────────────────────────
#  HELPERS DE FORMATO
# ─────────────────────────────────────────────
def fmt_cop(v):
    if v is None: return "Sin datos"
    return f"$ {int(v):,}".replace(",", ".")


def fmt_fecha(iso):
    if not iso: return "—"
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return iso


def diferencia_badge(hv, av):
    if hv is None or av is None:
        return "<span class='badge-eq'>Sin datos</span>", 0
    d = int(av) - int(hv)
    if d > 0:   return f"<span class='badge-up'>▲ +{abs(d):,}".replace(",", ".") + "</span>", d
    elif d < 0: return f"<span class='badge-down'>▼ -{abs(d):,}".replace(",", ".") + "</span>", d
    return "<span class='badge-eq'>= Igual</span>", 0


# ─────────────────────────────────────────────
#  PLANTILLA NEQUI HTML
# ─────────────────────────────────────────────
def render_plantilla(
    fecha_sup, reg_sup, cli_sup,
    fecha_inf, reg_inf, cli_inf
):
    badge_reg, dif_reg = diferencia_badge(reg_sup, reg_inf)
    badge_cli, dif_cli = diferencia_badge(cli_sup, cli_inf)

    hora = datetime.now().strftime("%H:%M")
    fs = fecha_sup if fecha_sup else "—"

    # Resumen comparativo
    def dir_texto(d): return "por encima" if d > 0 else "por debajo" if d < 0 else "igual"
    comp_html = ""
    if reg_sup and reg_inf and cli_sup and cli_inf:
        comp_html = f"""
        <div class='banner-comp'>
          El reporte muestra que actualmente en
          <b>Registro de Transacciones</b> estamos <b>{dir_texto(dif_reg)}</b>
          con una diferencia de <b>{fmt_cop(abs(dif_reg))}</b> y en
          <b>Transacciones de Clientes</b> estamos <b>{dir_texto(dif_cli)}</b>
          con una diferencia de <b>{fmt_cop(abs(dif_cli))}</b>.
        </div>"""

    html = f"""
    <!-- BLOQUE SUPERIOR -->
    <div style='border:2px solid #fff; background:#200020; margin-bottom:0;'>
      <div style='display:flex; align-items:center; justify-content:space-between;
                  padding:10px 16px; border-bottom:2px solid #fff;'>
        <div><span class='logo-dot'></span><span class='logo-nequi'>Nequi</span></div>
        <div style='color:#fff;font-size:18px;font-weight:700;'>{fs}</div>
      </div>
      <div class='nequi-title-pink'>TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00</div>
      <table class='nequi-table' style='border-top:none;'>
        <thead><tr><th style='width:65%'>SERVICIO</th><th>VALOR</th></tr></thead>
        <tbody>
          <tr>
            <td>REGISTRO DE TRANSACCIONES</td>
            <td class='valor'>$ &nbsp;{fmt_cop(reg_sup).replace('$ ','') if reg_sup else '<span style="color:#664466">Sin datos</span>'}</td>
          </tr>
          <tr>
            <td>TRANSACCIONES DE CLIENTES</td>
            <td class='valor'>$ &nbsp;{fmt_cop(cli_sup).replace('$ ','') if cli_sup else '<span style="color:#664466">Sin datos</span>'}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- SEPARADOR -->
    <div style='height:10px; background:#140014; border-left:2px solid #fff; border-right:2px solid #fff;'></div>

    <!-- BLOQUE INFERIOR -->
    <div style='border:2px solid #fff; background:#200020; border-top:none;'>
      <div style='display:flex; align-items:center; justify-content:space-between;
                  padding:10px 16px; border-bottom:2px solid #fff;'>
        <div><span class='logo-dot'></span><span class='logo-nequi'>Nequi</span></div>
        <div style='color:#fff;font-size:18px;font-weight:700;'>{fecha_inf}</div>
      </div>
      <div class='nequi-title-pink'>TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00</div>
      <table class='nequi-table' style='border-top:none;'>
        <thead><tr><th style='width:65%'>SERVICIO</th><th>VALOR</th></tr></thead>
        <tbody>
          <tr>
            <td>REGISTRO DE TRANSACCIONES</td>
            <td class='valor'>$ &nbsp;{fmt_cop(reg_inf).replace('$ ','') if reg_inf else '<span style="color:#664466">Sin datos</span>'}
              &nbsp;{badge_reg if reg_inf else ''}</td>
          </tr>
          <tr>
            <td>TRANSACCIONES DE CLIENTES</td>
            <td class='valor'>$ &nbsp;{fmt_cop(cli_inf).replace('$ ','') if cli_inf else '<span style="color:#664466">Sin datos</span>'}
              &nbsp;{badge_cli if cli_inf else ''}</td>
          </tr>
        </tbody>
      </table>
    </div>
    {comp_html}
    """
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  GRAFICA PLOTLY
# ─────────────────────────────────────────────
def render_grafica(datos_actuales, historico_map):
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="#200020",
        plot_bgcolor="#200020",
        font=dict(color="#CC88CC", family="Calibri, Arial", size=11),
        title=dict(text="Transaccionalidad — Comparativo histórico vs actual",
                   font=dict(color="#ffffff", size=14), x=0.5),
        legend=dict(bgcolor="#200020", bordercolor="#500050", borderwidth=1,
                    font=dict(color="#ccc", size=11)),
        xaxis=dict(gridcolor="rgba(255,0,170,0.12)", tickfont=dict(color="#CC88CC"),
                   linecolor="#500050", zerolinecolor="#500050"),
        yaxis=dict(gridcolor="rgba(255,0,170,0.12)", tickfont=dict(color="#CC88CC"),
                   linecolor="#500050", zerolinecolor="#500050",
                   tickformat="$,.0f"),
        hovermode="x unified",
        height=380,
        margin=dict(l=60, r=20, t=50, b=40)
    )

    franjas = FRANJAS_ACTUAL
    sup_reg = [historico_map.get(franja_sup(f), {}).get("registro_transacciones") for f in franjas]
    sup_cli = [historico_map.get(franja_sup(f), {}).get("transacciones_clientes")  for f in franjas]
    act_reg = [next((d["registro_transacciones"] for d in datos_actuales if d["franja"] == f), None) for f in franjas]
    act_cli = [next((d["transacciones_clientes"]  for d in datos_actuales if d["franja"] == f), None) for f in franjas]

    def none_to_none(lst):
        return [None if v is None else int(v) for v in lst]

    fig.add_trace(go.Scatter(
        x=franjas, y=none_to_none(sup_reg), name="Reg. Transacciones — Histórico",
        line=dict(color="#FF00AA", width=2), mode="lines+markers",
        marker=dict(size=7, color="#FF00AA"),
        connectgaps=False
    ))
    fig.add_trace(go.Scatter(
        x=franjas, y=none_to_none(sup_cli), name="Transac. Clientes — Histórico",
        line=dict(color="#00FFCC", width=2), mode="lines+markers",
        marker=dict(size=7, color="#00FFCC"),
        connectgaps=False
    ))
    fig.add_trace(go.Scatter(
        x=franjas, y=none_to_none(act_reg), name="Reg. Transacciones — Actual",
        line=dict(color="#FF6EE7", width=2, dash="dash"), mode="lines+markers",
        marker=dict(size=7, color="#FF6EE7", symbol="diamond"),
        connectgaps=False
    ))
    fig.add_trace(go.Scatter(
        x=franjas, y=none_to_none(act_cli), name="Transac. Clientes — Actual",
        line=dict(color="#00CCAA", width=2, dash="dash"), mode="lines+markers",
        marker=dict(size=7, color="#00CCAA", symbol="diamond"),
        connectgaps=False
    ))

    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  ENVIO TEAMS
# ─────────────────────────────────────────────
def enviar_teams(franja_inf, franja_sup_key, hist, act, comentario=""):
    fecha_hoy = date.today().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M")
    hist_reg = hist.get("registro_transacciones") if hist else None
    hist_cli = hist.get("transacciones_clientes")  if hist else None
    act_reg  = act.get("registro_transacciones")  if act  else None
    act_cli  = act.get("transacciones_clientes")   if act  else None
    fecha_hist = fmt_fecha(hist.get("fecha_reporte")) if hist else "—"

    def est(hv, av):
        if hv is None or av is None: return "Sin comparativo"
        d = int(av) - int(hv)
        return f"{'▲ Por encima' if d >= 0 else '▼ Por debajo'} ({fmt_cop(abs(d))})"

    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard", "version": "1.4",
                "body": [
                    {"type": "ColumnSet", "style": "emphasis", "bleed": True,
                     "columns": [
                         {"type": "Column", "width": "auto", "items": [{"type": "TextBlock", "text": "· Nequi", "weight": "Bolder", "size": "ExtraLarge", "color": "Light"}]},
                         {"type": "Column", "width": "stretch", "verticalContentAlignment": "Center",
                          "items": [{"type": "TextBlock", "text": fecha_hist, "weight": "Bolder", "size": "Large", "horizontalAlignment": "Center", "color": "Light"}]}
                     ]},
                    {"type": "TextBlock", "text": "TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00",
                     "weight": "Bolder", "color": "Accent", "horizontalAlignment": "Center", "spacing": "Small"},
                    {"type": "Table", "columns": [{"width": 2}, {"width": 1}], "rows": [
                        {"type": "TableRow", "style": "emphasis", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "SERVICIO", "weight": "Bolder", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "VALOR", "weight": "Bolder", "color": "Light", "horizontalAlignment": "Right"}]}]},
                        {"type": "TableRow", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "REGISTRO DE TRANSACCIONES", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": fmt_cop(hist_reg), "color": "Light", "horizontalAlignment": "Right"}]}]},
                        {"type": "TableRow", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "TRANSACCIONES DE CLIENTES", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": fmt_cop(hist_cli), "color": "Light", "horizontalAlignment": "Right"}]}]}
                    ]},
                    {"type": "ColumnSet", "style": "emphasis", "spacing": "Medium",
                     "columns": [
                         {"type": "Column", "width": "auto", "items": [{"type": "TextBlock", "text": "· Nequi", "weight": "Bolder", "size": "ExtraLarge", "color": "Light"}]},
                         {"type": "Column", "width": "stretch", "verticalContentAlignment": "Center",
                          "items": [{"type": "TextBlock", "text": fecha_hoy, "weight": "Bolder", "size": "Large", "horizontalAlignment": "Center", "color": "Light"}]}
                     ]},
                    {"type": "TextBlock", "text": "TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00",
                     "weight": "Bolder", "color": "Accent", "horizontalAlignment": "Center", "spacing": "Small"},
                    {"type": "Table", "columns": [{"width": 2}, {"width": 1}], "rows": [
                        {"type": "TableRow", "style": "emphasis", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "SERVICIO", "weight": "Bolder", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "VALOR", "weight": "Bolder", "color": "Light", "horizontalAlignment": "Right"}]}]},
                        {"type": "TableRow", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "REGISTRO DE TRANSACCIONES", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": fmt_cop(act_reg), "color": "Light", "horizontalAlignment": "Right"}]}]},
                        {"type": "TableRow", "cells": [
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": "TRANSACCIONES DE CLIENTES", "color": "Light"}]},
                            {"type": "TableCell", "items": [{"type": "TextBlock", "text": fmt_cop(act_cli), "color": "Light", "horizontalAlignment": "Right"}]}]}
                    ]},
                    {"type": "TextBlock",
                     "text": f"Para la fecha {fecha_hoy}, el reporte generado a las {hora} muestra:",
                     "weight": "Bolder", "spacing": "Medium", "wrap": True},
                    {"type": "FactSet", "facts": [
                        {"title": "Reg. Transacciones:", "value": est(hist_reg, act_reg)},
                        {"title": "Transac. Clientes:",  "value": est(hist_cli, act_cli)}
                    ]},
                    *([{"type": "TextBlock", "text": f"Observacion: {comentario}",
                        "wrap": True, "isSubtle": True, "spacing": "Small"}] if comentario else [])
                ]
            }
        }]
    }
    try:
        resp = requests.post(WEBHOOK_URL, headers={"Content-Type": "application/json"},
                             data=json.dumps(payload), timeout=15)
        ok = resp.ok
        registrar_envio(franja_inf, "OK" if ok else f"ERROR_{resp.status_code}", resp.text)
        return ok, resp.status_code
    except Exception as e:
        registrar_envio(franja_inf, "ERROR_RED", str(e))
        return False, str(e)


# ─────────────────────────────────────────────
#  HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div style='display:flex; align-items:center; justify-content:space-between;
            border-bottom:2px solid #FF00AA; padding-bottom:10px; margin-bottom:20px;'>
  <div>
    <span style='display:inline-block;width:10px;height:10px;background:#FF3355;
                 border-radius:50%;margin-right:4px;margin-bottom:10px;vertical-align:top;'></span>
    <span style='color:#fff;font-size:32px;font-weight:900;font-family:Calibri,Arial;'>Nequi</span>
  </div>
  <div style='color:#FF00AA;font-size:13px;font-weight:900;letter-spacing:0.5px;'>
    SISTEMA DE TRANSACCIONALIDAD
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS PRINCIPALES
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 PLANTILLA",
    "📝 INGRESAR DATOS",
    "📈 GRÁFICA",
    "📤 ENVIAR A TEAMS"
])

# ══════════════════════════════════════════════
#  TAB 1 — PLANTILLA VISUAL
# ══════════════════════════════════════════════
with tab1:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        franja_h = st.selectbox("FRANJA HISTÓRICA", FRANJAS_HISTORICO, key="sel_h")
    with col_sel2:
        franja_a = st.selectbox("FRANJA ACTUAL", FRANJAS_ACTUAL, key="sel_a")

    hist = obtener_historico(franja_h)
    act  = obtener_actual(franja_a)

    fecha_sup_val = fmt_fecha(hist.get("fecha_reporte")) if hist else "—"
    fecha_inf_val = date.today().strftime("%d/%m/%Y")
    reg_sup_val   = hist.get("registro_transacciones") if hist else None
    cli_sup_val   = hist.get("transacciones_clientes")  if hist else None
    reg_inf_val   = act.get("registro_transacciones")  if act  else None
    cli_inf_val   = act.get("transacciones_clientes")   if act  else None

    render_plantilla(
        fecha_sup_val, reg_sup_val, cli_sup_val,
        fecha_inf_val, reg_inf_val, cli_inf_val
    )

# ══════════════════════════════════════════════
#  TAB 2 — INGRESAR DATOS
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### DATOS HISTÓRICOS — Bloque superior (cada 8h)")
    col1, col2, col3 = st.columns(3)
    with col1:
        fh = st.selectbox("Franja histórica", FRANJAS_HISTORICO, key="inp_fh")
    with col2:
        fecha_h = st.date_input("Fecha del reporte", value=date.today(), key="inp_fecha_h")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        reg_h = st.number_input("Registro de Transacciones ($)", min_value=0, step=1000, key="inp_reg_h", format="%d")
    with col5:
        cli_h = st.number_input("Transacciones de Clientes ($)", min_value=0, step=1000, key="inp_cli_h", format="%d")

    if st.button("GUARDAR HISTÓRICO", key="btn_guardar_h"):
        if reg_h > 0 or cli_h > 0:
            guardar_historico(fh, fecha_h.isoformat(), reg_h, cli_h)
            st.success(f"✓ Histórico guardado — franja {fh} | {fecha_h.strftime('%d/%m/%Y')}")
            st.cache_resource.clear()
        else:
            st.warning("Ingresa al menos un valor mayor a cero.")

    st.markdown("---")
    st.markdown("### REGISTRO ACTUAL — Bloque inferior (cada 2h)")

    col6, col7 = st.columns([1, 3])
    with col6:
        fa = st.selectbox("Franja actual", FRANJAS_ACTUAL, key="inp_fa")
    with col7:
        st.markdown("<br>", unsafe_allow_html=True)

    col8, col9 = st.columns(2)
    with col8:
        reg_a = st.number_input("Registro de Transacciones ($)", min_value=0, step=1000, key="inp_reg_a", format="%d")
    with col9:
        cli_a = st.number_input("Transacciones de Clientes ($)", min_value=0, step=1000, key="inp_cli_a", format="%d")

    if st.button("GUARDAR REGISTRO ACTUAL", key="btn_guardar_a"):
        if reg_a > 0 or cli_a > 0:
            guardar_actual(fa, reg_a, cli_a)
            st.success(f"✓ Registro actual guardado — franja {fa} | {date.today().strftime('%d/%m/%Y')}")
            st.cache_resource.clear()
        else:
            st.warning("Ingresa al menos un valor mayor a cero.")

# ══════════════════════════════════════════════
#  TAB 3 — GRÁFICA
# ══════════════════════════════════════════════
with tab3:
    datos_act = obtener_todos_actual()
    hist_map = {}
    for fk in FRANJAS_HISTORICO:
        h = obtener_historico(fk)
        if h:
            hist_map[fk] = h

    if not datos_act and not hist_map:
        st.info("Aún no hay datos registrados. Ve a la pestaña INGRESAR DATOS para comenzar.")
    else:
        render_grafica(datos_act, hist_map)

        st.markdown("---")
        st.markdown("##### Resumen del día")
        cols = st.columns(len(FRANJAS_ACTUAL))
        for i, f in enumerate(FRANJAS_ACTUAL):
            act_d = next((d for d in datos_act if d["franja"] == f), None)
            fk    = franja_sup(f)
            hst   = hist_map.get(fk)
            with cols[i]:
                if act_d:
                    dif_r = (int(act_d["registro_transacciones"]) - int(hst["registro_transacciones"])) if hst else None
                    st.metric(
                        label=f,
                        value=fmt_cop(act_d["registro_transacciones"]),
                        delta=f"+{fmt_cop(dif_r)}" if dif_r and dif_r > 0 else fmt_cop(dif_r) if dif_r else None
                    )
                else:
                    st.metric(label=f, value="—")

# ══════════════════════════════════════════════
#  TAB 4 — ENVIAR A TEAMS
# ══════════════════════════════════════════════
with tab4:
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        franja_env = st.selectbox("Franja a enviar", FRANJAS_ACTUAL, key="sel_env")
    with col_e2:
        comentario = st.text_input("Comentario adicional (opcional)", key="comentario_env",
                                   placeholder="Ej: Se recomienda reforzar canales digitales...")

    fk_env   = franja_sup(franja_env)
    hist_env = obtener_historico(fk_env)
    act_env  = obtener_actual(franja_env)

    fecha_hoy_str = date.today().strftime("%d/%m/%Y")
    hora_str      = datetime.now().strftime("%H:%M")
    fecha_h_str   = fmt_fecha(hist_env.get("fecha_reporte")) if hist_env else "—"

    st.markdown("---")
    st.markdown("##### Vista previa del mensaje")

    reg_h_v = hist_env.get("registro_transacciones") if hist_env else None
    cli_h_v = hist_env.get("transacciones_clientes")  if hist_env else None
    reg_a_v = act_env.get("registro_transacciones")  if act_env  else None
    cli_a_v = act_env.get("transacciones_clientes")   if act_env  else None

    def est_txt(hv, av):
        if hv is None or av is None: return "Sin comparativo"
        d = int(av) - int(hv)
        return f"{'▲ Por encima' if d >= 0 else '▼ Por debajo'} ({fmt_cop(abs(d))})"

    preview = f"""
📊 Para la fecha **{fecha_hoy_str}**, el reporte generado a las **{hora_str}** muestra:

• **Registro de Transacciones:** {est_txt(reg_h_v, reg_a_v)}
  (actual: {fmt_cop(reg_a_v)} vs histórico: {fmt_cop(reg_h_v)} del {fecha_h_str} franja {fk_env})

• **Transacciones de Clientes:** {est_txt(cli_h_v, cli_a_v)}
  (actual: {fmt_cop(cli_a_v)} vs histórico: {fmt_cop(cli_h_v)} del {fecha_h_str} franja {fk_env})
"""
    if comentario:
        preview += f"\n💬 {comentario}"

    st.markdown(preview)
    st.markdown("---")

    if st.button("ENVIAR A TEAMS 📤", key="btn_teams"):
        if not WEBHOOK_URL:
            st.error("El Webhook URL no está configurado en los secrets.")
        else:
            with st.spinner("Enviando a Teams..."):
                ok, code = enviar_teams(franja_env, fk_env, hist_env or {}, act_env or {}, comentario)
            if ok:
                st.success(f"✓ Enviado correctamente a Teams — {hora_str}")
            else:
                st.error(f"✗ Error al enviar: {code}")
