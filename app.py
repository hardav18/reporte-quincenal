import streamlit as st
import requests
import json
from datetime import datetime, date
import plotly.graph_objects as go

st.set_page_config(page_title="Nequi — Transaccionalidad", page_icon="💜", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');
html,body,[class*="css"]{background-color:#200020!important;color:#fff!important;font-family:Calibri,'Nunito',Arial,sans-serif!important;}
.stApp{background-color:#200020!important;}
[data-testid="manage-app-button"],.stAppDeployButton,footer,#MainMenu{display:none!important;}

/* ---- SELECTBOX fondo oscuro + texto blanco ---- */
div[data-baseweb="select"] > div{background-color:#300030!important;border:1px solid #FF00AA!important;color:#ffffff!important;}
div[data-baseweb="select"] span{color:#ffffff!important;}
div[data-baseweb="select"] svg{fill:#FF00AA!important;}
/* Dropdown lista desplegable */
div[data-baseweb="popover"] *{background-color:#300030!important;color:#ffffff!important;}
div[data-baseweb="menu"] li{background-color:#300030!important;color:#ffffff!important;}
div[data-baseweb="menu"] li:hover{background-color:#500050!important;color:#FF00AA!important;}
div[data-baseweb="option"]{background-color:#300030!important;color:#ffffff!important;}
div[data-baseweb="option"]:hover{background-color:#500050!important;color:#FF00AA!important;}
[data-baseweb="select"] [aria-selected="true"]{background-color:#400040!important;color:#FF00AA!important;}

/* ---- Labels ---- */
label,.stSelectbox label,.stNumberInput label,.stDateInput label,.stCheckbox label,.stTextInput label{color:#FF00AA!important;font-weight:900!important;font-size:12px!important;}

/* ---- Botones ---- */
.stButton>button{background-color:#FF00AA!important;color:#fff!important;border:none!important;border-radius:4px!important;font-weight:900!important;padding:8px 20px;}
.stButton>button:hover{background-color:#CC0088!important;}

/* ---- Inputs numéricos / texto ---- */
input[type="number"],input[type="text"]{background-color:#300030!important;color:#fff!important;border:1px solid #FF00AA!important;border-radius:4px!important;}

/* ---- DateInput ---- */
.stDateInput>div>div>input{background-color:#300030!important;color:#fff!important;border:1px solid #FF00AA!important;}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{background-color:#200020!important;border-bottom:2px solid #FF00AA!important;}
.stTabs [data-baseweb="tab"]{background-color:#200020!important;color:#886688!important;font-weight:900!important;font-size:12px!important;}
.stTabs [aria-selected="true"]{background-color:#2a002a!important;color:#FF00AA!important;border-bottom:2px solid #FF00AA!important;}

/* ---- Métricas ---- */
[data-testid="metric-container"]{background-color:#2a002a!important;border:1px solid #500050!important;border-radius:6px!important;padding:10px!important;}
[data-testid="metric-container"] label{color:#FF00AA!important;font-size:10px!important;font-weight:900!important;}
[data-testid="stMetricValue"]{color:#fff!important;font-size:15px!important;font-weight:700!important;}

/* ---- Alerts ---- */
.stSuccess{background-color:#003300!important;border-color:#00AA44!important;}
.stError{background-color:#330000!important;border-color:#CC2222!important;}
hr{border-color:#500050!important;}
p,li,span{color:#fff!important;}
h1,h2,h3{color:#FF00AA!important;font-weight:900!important;}

/* ---- Tabla Nequi ---- */
.nequi-table{width:100%;border-collapse:collapse;background:#200020;border:2px solid #fff;font-family:Calibri,Arial,sans-serif;}
.nequi-table th{background:#2a002a;color:#fff;font-size:13px;font-weight:900;padding:9px 14px;border:1px solid #fff;text-transform:uppercase;}
.nequi-table td{color:#fff;font-size:13px;font-weight:700;padding:9px 14px;border:1px solid #fff;}
.nequi-table td.valor{text-align:right;font-size:14px;}
.nequi-title-pink{color:#FF00AA;text-align:center;font-size:13px;font-weight:900;letter-spacing:0.4px;padding:7px;border:1px solid #fff;border-top:none;background:#200020;}
.logo-nequi{font-size:26px;font-weight:900;color:#fff;font-family:Calibri,Arial,sans-serif;}
.logo-dot{display:inline-block;width:9px;height:9px;background:#FF3355;border-radius:50%;margin-right:2px;margin-bottom:12px;vertical-align:top;}
.badge-up{background:#00AA44;color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:900;}
.badge-down{background:#CC2222;color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;font-weight:900;}
.banner-comp{background:#1a001a;border:1px solid #FF00AA;border-radius:4px;padding:14px 18px;margin-top:12px;}
.banner-comp p{color:#ffffff!important;font-size:14px!important;font-weight:700!important;line-height:1.8!important;margin:0;}
.banner-comp b{color:#FF00AA!important;}
</style>
""", unsafe_allow_html=True)

WEBHOOK_URL  = st.secrets.get("WEBHOOK_URL",  "")
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

# Ambas franjas usan las 7 horas completas
FRANJAS = ["08:00","10:00","12:00","14:00","16:00","18:00","20:00"]

@st.cache_resource
def get_sb():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_historico(franja, fecha_reporte, reg, cli):
    get_sb().table("historico").insert({"franja":franja,"fecha_reporte":fecha_reporte,"registro_transacciones":reg,"transacciones_clientes":cli}).execute()

def obtener_historico(franja):
    r = get_sb().table("historico").select("*").eq("franja",franja).order("id",desc=True).limit(1).execute()
    return r.data[0] if r.data else None

def guardar_actual(franja, reg, cli):
    hoy = date.today().isoformat()
    sb  = get_sb()
    ex  = sb.table("registro_actual").select("id").eq("franja",franja).eq("fecha",hoy).execute()
    data = {"franja":franja,"fecha":hoy,"registro_transacciones":reg,"transacciones_clientes":cli}
    if ex.data: sb.table("registro_actual").update(data).eq("franja",franja).eq("fecha",hoy).execute()
    else:       sb.table("registro_actual").insert(data).execute()

def obtener_actual(franja):
    hoy = date.today().isoformat()
    r   = get_sb().table("registro_actual").select("*").eq("franja",franja).eq("fecha",hoy).execute()
    return r.data[0] if r.data else None

def obtener_todos_actual():
    hoy = date.today().isoformat()
    r   = get_sb().table("registro_actual").select("*").eq("fecha",hoy).order("franja").execute()
    return r.data or []

def registrar_envio(franja, estado, resp):
    try: get_sb().table("log_envios").insert({"franja":franja,"fecha":date.today().isoformat(),"estado":estado,"respuesta":resp[:200]}).execute()
    except: pass

def fmt_cop(v):
    if v is None: return "Sin datos"
    return f"$ {int(v):,}".replace(",",".")

def fmt_fecha(iso):
    if not iso: return "—"
    try: y,m,d=iso.split("-"); return f"{d}/{m}/{y}"
    except: return iso

def dif_badge(hv, av):
    if hv is None or av is None: return "",0
    d=int(av)-int(hv)
    if d>0:  return f"<span class='badge-up'>▲ +{abs(d):,}".replace(",",".")+"</span>",d
    elif d<0:return f"<span class='badge-down'>▼ -{abs(d):,}".replace(",",".")+"</span>",d
    return "",0

def render_plantilla(f_sup, reg_sup, cli_sup, f_inf, reg_inf, cli_inf):
    b_reg,d_reg = dif_badge(reg_sup,reg_inf)
    b_cli,d_cli = dif_badge(cli_sup,cli_inf)
    def vhtml(v,badge=""):
        num = fmt_cop(v).replace("$ ","") if v is not None else '<span style="color:#664466">Sin datos</span>'
        return f'$ &nbsp;{num}&nbsp;{badge}'
    def dirt(d): return "por encima" if d>0 else "por debajo" if d<0 else "igual"
    comp=""
    if reg_sup and reg_inf and cli_sup and cli_inf:
        comp=f"""<div class='banner-comp'><p>El reporte muestra que actualmente en
        <b>Registro de Transacciones</b> estamos <b>{dirt(d_reg)}</b> con una diferencia de <b>{fmt_cop(abs(d_reg))}</b>
        y en <b>Transacciones de Clientes</b> estamos <b>{dirt(d_cli)}</b> con una diferencia de <b>{fmt_cop(abs(d_cli))}</b>.</p></div>"""
    st.markdown(f"""
    <div style='border:2px solid #fff;background:#200020;'>
      <div style='display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:2px solid #fff;'>
        <div><span class='logo-dot'></span><span class='logo-nequi'>Nequi</span></div>
        <div style='color:#fff;font-size:18px;font-weight:700;'>{f_sup if f_sup else "—"}</div>
      </div>
      <div class='nequi-title-pink'>TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00</div>
      <table class='nequi-table' style='border-top:none;'>
        <thead><tr><th style='width:65%'>SERVICIO</th><th>VALOR</th></tr></thead>
        <tbody>
          <tr><td>REGISTRO DE TRANSACCIONES</td><td class='valor'>{vhtml(reg_sup)}</td></tr>
          <tr><td>TRANSACCIONES DE CLIENTES</td><td class='valor'>{vhtml(cli_sup)}</td></tr>
        </tbody>
      </table>
    </div>
    <div style='height:10px;background:#140014;border-left:2px solid #fff;border-right:2px solid #fff;'></div>
    <div style='border:2px solid #fff;background:#200020;border-top:none;'>
      <div style='display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:2px solid #fff;'>
        <div><span class='logo-dot'></span><span class='logo-nequi'>Nequi</span></div>
        <div style='color:#fff;font-size:18px;font-weight:700;'>{f_inf}</div>
      </div>
      <div class='nequi-title-pink'>TRANSACCIONALIDAD ENTRE LAS 00:00 Y LAS 20:00</div>
      <table class='nequi-table' style='border-top:none;'>
        <thead><tr><th style='width:65%'>SERVICIO</th><th>VALOR</th></tr></thead>
        <tbody>
          <tr><td>REGISTRO DE TRANSACCIONES</td><td class='valor'>{vhtml(reg_inf,b_reg)}</td></tr>
          <tr><td>TRANSACCIONES DE CLIENTES</td><td class='valor'>{vhtml(cli_inf,b_cli)}</td></tr>
        </tbody>
      </table>
    </div>
    {comp}""", unsafe_allow_html=True)

def render_grafica(datos_act, hist_map):
    fig=go.Figure()
    sup_reg=[hist_map.get(f,{}).get("registro_transacciones") for f in FRANJAS]
    sup_cli=[hist_map.get(f,{}).get("transacciones_clientes")  for f in FRANJAS]
    act_reg=[next((d["registro_transacciones"] for d in datos_act if d["franja"]==f),None) for f in FRANJAS]
    act_cli=[next((d["transacciones_clientes"]  for d in datos_act if d["franja"]==f),None) for f in FRANJAS]
    ni=lambda lst:[None if v is None else int(v) for v in lst]
    fig.add_trace(go.Scatter(x=FRANJAS,y=ni(sup_reg),name="Reg.Transacciones — Histórico",line=dict(color="#FF00AA",width=2),mode="lines+markers",marker=dict(size=7),connectgaps=False))
    fig.add_trace(go.Scatter(x=FRANJAS,y=ni(sup_cli),name="Transac.Clientes — Histórico",line=dict(color="#00FFCC",width=2),mode="lines+markers",marker=dict(size=7),connectgaps=False))
    fig.add_trace(go.Scatter(x=FRANJAS,y=ni(act_reg),name="Reg.Transacciones — Actual",line=dict(color="#FF6EE7",width=2,dash="dash"),mode="lines+markers",marker=dict(size=7,symbol="diamond"),connectgaps=False))
    fig.add_trace(go.Scatter(x=FRANJAS,y=ni(act_cli),name="Transac.Clientes — Actual",line=dict(color="#00CCAA",width=2,dash="dash"),mode="lines+markers",marker=dict(size=7,symbol="diamond"),connectgaps=False))
    fig.update_layout(paper_bgcolor="#200020",plot_bgcolor="#200020",font=dict(color="#CC88CC",family="Calibri,Arial",size=11),
        title=dict(text="Transaccionalidad — Comparativo histórico vs actual",font=dict(color="#fff",size=14),x=0.5),
        legend=dict(bgcolor="#200020",bordercolor="#500050",borderwidth=1,font=dict(color="#ccc",size=11)),
        xaxis=dict(gridcolor="rgba(255,0,170,0.15)",tickfont=dict(color="#CC88CC"),linecolor="#500050"),
        yaxis=dict(gridcolor="rgba(255,0,170,0.15)",tickfont=dict(color="#CC88CC"),linecolor="#500050",tickformat="$,.0f"),
        hovermode="x unified",height=380,margin=dict(l=60,r=20,t=50,b=40))
    st.plotly_chart(fig,use_container_width=True)

def enviar_teams(franja_inf, hist, act, comentario="", incluir_comentario=False):
    fecha_hoy = date.today().strftime("%d/%m/%Y")
    hora      = datetime.now().strftime("%H:%M")
    hr  = hist.get("registro_transacciones") if hist else None
    hc  = hist.get("transacciones_clientes")  if hist else None
    ar  = act.get("registro_transacciones")  if act  else None
    ac  = act.get("transacciones_clientes")   if act  else None
    fh  = fmt_fecha(hist.get("fecha_reporte")) if hist else "—"
    fhi = franja_inf

    def est(hv,av):
        if hv is None or av is None: return "Sin comparativo"
        d=int(av)-int(hv)
        return f"{'▲ Por encima' if d>=0 else '▼ Por debajo'} ({fmt_cop(abs(d))})"

    # Colores en hex para Teams (MessageCard legacy — soporta colores reales)
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "FF00AA",
        "summary": "Nequi — Reporte de Transaccionalidad",
        "sections": [
            {
                "activityTitle": f"<span style='color:#FF00AA;font-size:20px;font-weight:900'>· Nequi</span>",
                "activitySubtitle": f"Reporte — {fecha_hoy} | Franja: {fhi}",
                "activityImage": "",
                "facts": [],
                "markdown": True
            },
            {
                "title": f"📅 HISTÓRICO — {fh}",
                "facts": [
                    {"name": "Registro de Transacciones:", "value": fmt_cop(hr)},
                    {"name": "Transacciones de Clientes:",  "value": fmt_cop(hc)}
                ],
                "markdown": True
            },
            {
                "title": f"📅 REGISTRO ACTUAL — {fecha_hoy} {fhi}",
                "facts": [
                    {"name": "Registro de Transacciones:", "value": fmt_cop(ar)},
                    {"name": "Transacciones de Clientes:",  "value": fmt_cop(ac)}
                ],
                "markdown": True
            },
            {
                "title": "📊 COMPARATIVO",
                "facts": [
                    {"name": "Reg. Transacciones:", "value": est(hr,ar)},
                    {"name": "Transac. Clientes:",  "value": est(hc,ac)}
                ],
                "text": f"Para la fecha **{fecha_hoy}**, el reporte generado a las **{hora}** muestra los resultados comparativos indicados arriba, referenciando el histórico del **{fh}** franja **{fhi}**." + (f"\n\n💬 {comentario}" if incluir_comentario and comentario.strip() else ""),
                "markdown": True
            }
        ]
    }
    try:
        resp=requests.post(WEBHOOK_URL,headers={"Content-Type":"application/json"},data=json.dumps(payload),timeout=15)
        ok=resp.ok
        registrar_envio(franja_inf,"OK" if ok else f"ERROR_{resp.status_code}",resp.text)
        return ok,resp.status_code
    except Exception as e:
        registrar_envio(franja_inf,"ERROR_RED",str(e))
        return False,str(e)

# ── Header
st.markdown("""
<div style='display:flex;align-items:center;justify-content:space-between;
            border-bottom:2px solid #FF00AA;padding-bottom:10px;margin-bottom:20px;'>
  <div><span style='display:inline-block;width:10px;height:10px;background:#FF3355;border-radius:50%;
             margin-right:4px;margin-bottom:10px;vertical-align:top;'></span>
    <span style='color:#fff;font-size:32px;font-weight:900;font-family:Calibri,Arial;'>Nequi</span></div>
  <div style='color:#FF00AA;font-size:13px;font-weight:900;letter-spacing:0.5px;'>SISTEMA DE TRANSACCIONALIDAD</div>
</div>""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4 = st.tabs(["📊 PLANTILLA","📝 INGRESAR DATOS","📈 GRÁFICA","📤 ENVIAR A TEAMS"])

# ══ TAB 1
with tab1:
    c1,c2=st.columns(2)
    with c1: fh=st.selectbox("FRANJA HISTÓRICA",FRANJAS,key="sel_h")
    with c2: fa=st.selectbox("FRANJA ACTUAL",FRANJAS,key="sel_a")
    hist=obtener_historico(fh); act=obtener_actual(fa)
    render_plantilla(
        fmt_fecha(hist.get("fecha_reporte")) if hist else "—",
        hist.get("registro_transacciones") if hist else None,
        hist.get("transacciones_clientes")  if hist else None,
        date.today().strftime("%d/%m/%Y"),
        act.get("registro_transacciones")  if act else None,
        act.get("transacciones_clientes")   if act else None
    )

# ══ TAB 2
with tab2:
    st.markdown("### DATOS HISTÓRICOS — Bloque superior")
    c1,c2=st.columns(2)
    with c1: fh2=st.selectbox("Franja histórica",FRANJAS,key="inp_fh")
    with c2: fecha_h=st.date_input("Fecha del reporte",value=date.today(),key="inp_fh_date")
    c3,c4=st.columns(2)
    with c3: reg_h=st.number_input("Registro de Transacciones ($)",min_value=0,step=1000,key="inp_reg_h",format="%d")
    with c4: cli_h=st.number_input("Transacciones de Clientes ($)", min_value=0,step=1000,key="inp_cli_h",format="%d")
    if st.button("GUARDAR HISTÓRICO"):
        if reg_h>0 or cli_h>0:
            guardar_historico(fh2,fecha_h.isoformat(),reg_h,cli_h)
            st.success(f"✓ Histórico guardado — franja {fh2} | {fecha_h.strftime('%d/%m/%Y')}")
            st.cache_resource.clear()
        else: st.warning("Ingresa al menos un valor mayor a cero.")
    st.markdown("---")
    st.markdown("### REGISTRO ACTUAL — Bloque inferior (cada 2h)")
    c5,_=st.columns([1,3])
    with c5: fa2=st.selectbox("Franja actual",FRANJAS,key="inp_fa")
    c6,c7=st.columns(2)
    with c6: reg_a=st.number_input("Registro de Transacciones ($)",min_value=0,step=1000,key="inp_reg_a",format="%d")
    with c7: cli_a=st.number_input("Transacciones de Clientes ($)", min_value=0,step=1000,key="inp_cli_a",format="%d")
    if st.button("GUARDAR REGISTRO ACTUAL"):
        if reg_a>0 or cli_a>0:
            guardar_actual(fa2,reg_a,cli_a)
            st.success(f"✓ Registro actual guardado — franja {fa2} | {date.today().strftime('%d/%m/%Y')}")
            st.cache_resource.clear()
        else: st.warning("Ingresa al menos un valor mayor a cero.")

# ══ TAB 3
with tab3:
    datos_act=obtener_todos_actual()
    hist_map={f:obtener_historico(f) for f in FRANJAS if obtener_historico(f)}
    if not datos_act and not hist_map:
        st.info("Sin datos aún. Ve a INGRESAR DATOS para comenzar.")
    else:
        render_grafica(datos_act,hist_map)
        st.markdown("---")
        st.markdown("##### Resumen del día por franja")
        cols=st.columns(len(FRANJAS))
        for i,f in enumerate(FRANJAS):
            act_d=next((d for d in datos_act if d["franja"]==f),None)
            hst=hist_map.get(f)
            with cols[i]:
                if act_d:
                    dif=(int(act_d["registro_transacciones"])-int(hst["registro_transacciones"])) if hst and hst.get("registro_transacciones") else None
                    st.metric(f,fmt_cop(act_d["registro_transacciones"]),delta=f"+{fmt_cop(dif)}" if dif and dif>0 else fmt_cop(dif) if dif else None)
                else: st.metric(f,"—")

# ══ TAB 4
with tab4:
    c1,_=st.columns(2)
    with c1: franja_env=st.selectbox("Franja a enviar",FRANJAS,key="sel_env")
    hist_env=obtener_historico(franja_env)
    act_env =obtener_actual(franja_env)
    fecha_hoy_s=date.today().strftime("%d/%m/%Y")
    hora_s=datetime.now().strftime("%H:%M")
    fh_s=fmt_fecha(hist_env.get("fecha_reporte")) if hist_env else "—"
    rh=hist_env.get("registro_transacciones") if hist_env else None
    ch=hist_env.get("transacciones_clientes")  if hist_env else None
    ra=act_env.get("registro_transacciones")  if act_env else None
    ca=act_env.get("transacciones_clientes")   if act_env else None
    def est2(hv,av):
        if hv is None or av is None: return "Sin comparativo"
        d=int(av)-int(hv)
        return f"{'▲ Por encima' if d>=0 else '▼ Por debajo'} ({fmt_cop(abs(d))})"
    st.markdown("---")
    st.markdown("##### Vista previa")
    st.markdown(f"""
Para la fecha **{fecha_hoy_s}**, el reporte generado a las **{hora_s}** muestra:

• **Registro de Transacciones:** {est2(rh,ra)}
*(actual: {fmt_cop(ra)} vs histórico: {fmt_cop(rh)} del {fh_s} — franja {franja_env})*

• **Transacciones de Clientes:** {est2(ch,ca)}
*(actual: {fmt_cop(ca)} vs histórico: {fmt_cop(ch)} del {fh_s} — franja {franja_env})*
""")
    st.markdown("---")
    incluir=st.checkbox("Incluir comentario adicional en el mensaje",value=False)
    comentario=""
    if incluir:
        comentario=st.text_input("Comentario adicional",placeholder="Ej: Se recomienda reforzar canales digitales...")
    st.markdown("---")
    if st.button("ENVIAR A TEAMS 📤"):
        if not WEBHOOK_URL:
            st.error("Webhook URL no configurado.")
        else:
            with st.spinner("Enviando a Teams..."):
                ok,code=enviar_teams(franja_env,hist_env or {},act_env or {},comentario,incluir)
            if ok: st.success(f"✓ Enviado correctamente — {hora_s}")
            else:  st.error(f"✗ Error: {code}")


