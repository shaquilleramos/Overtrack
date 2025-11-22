# procesamiento.py
import pandas as pd
from datetime import datetime, timedelta

# -------------------------
# HORARIOS (por sede y por día) - aquí defines las sedes y sus horarios por día
# -------------------------
HORARIOS_SEDES = {
    "medellin": {
        "Lunes": {"entrada": "08:00", "salida": "17:00"},
        "Martes": {"entrada": "08:00", "salida": "17:00"},
        "Miércoles": {"entrada": "08:00", "salida": "17:00"},
        "Jueves": {"entrada": "08:00", "salida": "17:00"},
        "Viernes": {"entrada": "08:00", "salida": "17:00"},
        "Sábado": {"entrada": "08:00", "salida": "17:00"},
    },
    "barranquilla": {
        "Lunes": {"entrada": "08:00", "salida": "17:00"},
        "Martes": {"entrada": "08:00", "salida": "17:00"},
        "Miércoles": {"entrada": "08:00", "salida": "17:00"},
        "Jueves": {"entrada": "08:00", "salida": "17:00"},
        "Viernes": {"entrada": "08:00", "salida": "16:00"},
        "Sábado": {"entrada": "09:00", "salida": "14:00"},

    },
    "cartagena": {
        "Lunes": {"entrada": "09:00", "salida": "17:30"},
        "Martes": {"entrada": "09:00", "salida": "17:30"},
        "Miércoles": {"entrada": "09:00", "salida": "17:30"},
        "Jueves": {"entrada": "09:00", "salida": "17:30"},
        "Viernes": {"entrada": "09:00", "salida": "17:30"},
        "Sábado": {"entrada": "09:00", "salida": "15:00"},

    }
}

# -------------------------
# MAPA DIAS (EN -> ES)
# -------------------------
DIAS_MAP = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}


# -------------------------
# Detectar columnas (nombre y fecha/hora)
# -------------------------
def detectar_columnas(df):

    # Índice fijo según tu archivo del huellero
    idx_nombre = 1  # Columna B
    idx_fecha  = 3  # Columna D

    # Validar que existan esas columnas
    if df.shape[1] <= max(idx_nombre, idx_fecha):
        raise ValueError("El archivo no tiene suficientes columnas para B y D")

    col_nombre = df.columns[idx_nombre]
    col_fecha  = df.columns[idx_fecha]

    return col_nombre, col_fecha

# Antiguo detectar_columnas (comentado)
# def detectar_columnas(df):
#     posibles_nombres = ['nombre', 'empleado', 'user name', 'usuario', 'person id', 'name']
#     posibles_fechas = ['fechahora', 'hora', 'time', 'fecha', 'datetime', 'timestamp', 'marcacion', 'check']

#     cols = [c.strip().lower() for c in df.columns]

#     col_nombre = next((orig for orig in df.columns if any(p in orig.lower() for p in posibles_nombres)), None)
#     col_fecha = next((orig for orig in df.columns if any(p in orig.lower() for p in posibles_fechas)), None)

#     return col_nombre, col_fecha


    posibles_nombres = ['nombre', 'empleado', 'user name', 'usuario', 'person id', 'name']
    posibles_fechas = ['fechahora', 'hora', 'time', 'fecha', 'datetime', 'timestamp', 'marcacion', 'check']

    cols = [c.strip().lower() for c in df.columns]

    col_nombre = next((orig for orig in df.columns if any(p in orig.lower() for p in posibles_nombres)), None)
    col_fecha = next((orig for orig in df.columns if any(p in orig.lower() for p in posibles_fechas)), None)

    return col_nombre, col_fecha



# -------------------------
# Formateador de timedeltas -> "H:MM" (00:00 si es 0)
# -------------------------

def calcular_extras(entrada_dt, salida_dt, entrada_oficial_dt, salida_oficial_dt, tardanza_td):
    """
    Opción A corregida con redondeo exacto.
    """

    # minutos antes de la entrada oficial
    if entrada_dt < entrada_oficial_dt:
        minutos_antes = (entrada_oficial_dt - entrada_dt)
    else:
        minutos_antes = timedelta(0)

    # minutos después de la salida oficial
    if salida_dt > salida_oficial_dt:
        minutos_despues = (salida_dt - salida_oficial_dt)
    else:
        minutos_despues = timedelta(0)

    # total bruto = antes + después
    total_bruto = minutos_antes + minutos_despues

    # restar tardanza
    total_neto = total_bruto - tardanza_td
    if total_neto < timedelta(0):
        total_neto = timedelta(0)

    # 🔥 Convertimos a minutos redondeados correctamente
    total_min = round(total_neto.total_seconds() / 60)

    # Exige mínimo 50 minutos
    if total_min < 50:
        return timedelta(0)

    # Regresamos el valor exacto
    return timedelta(minutes=total_min)




def formato_hhmm(td: timedelta) -> str:
    if not isinstance(td, timedelta):
        return "00h 00m"

    total_min = round(td.total_seconds() / 60)  # redondea minutos
    if total_min <= 0:
        return "00h 00m"

    h = total_min // 60
    m = total_min % 60
    return f"{h:02d}h {m:02d}m"



def formato_hhmm(td: timedelta) -> str:
    if td is None:
        return "--:--"
    total_min = int(td.total_seconds() // 60)
    if total_min <= 0:
        return "00:00"
    h = total_min // 60
    m = total_min % 60
    return f"{h:02d}:{m:02d}"

from datetime import timedelta

def calcular_extras(salida_dt, salida_oficial_dt, tardanza_td):
    """
    entrada:
      salida_dt: datetime (salida real)
      salida_oficial_dt: datetime (fin de jornada oficial para ese día)
      tardanza_td: timedelta (minutos de tardanza; puede ser timedelta(0))

    salida:
      extras_td: timedelta con el total de tiempo extra a contabilizar (0 si no aplica)
    Regla:
      neto = salida_dt - salida_oficial_dt - tardanza_td
      si neto < 50 minutos -> 0
      si neto >= 50 minutos -> extras = neto (se cuenta todo)
    """
    # Calcula la diferencia neta (puede ser negativa)
    neto = salida_dt - salida_oficial_dt - tardanza_td

    # Si neto negativo -> no hay extra
    if neto <= timedelta(0):
        return timedelta(0)

    # Si neto < 50 minutos -> no hay extra
    if neto < timedelta(minutes=50):
        return timedelta(0)

    # Si neto >= 50 minutos -> se cuenta todo
    return neto


def formatear_hhmm(td):
    """Devuelve 'HH:MM' (si td==0 devuelve '00:00')"""
    if not td or td <= timedelta(0):
        return "00:00"
    total_min = int(td.total_seconds() // 60)
    h = total_min // 60
    m = total_min % 60
    return f"{h:02d}:{m:02d}"


# -------------------------
# PROCESAR REGISTROS (función pública)
# recibe DataFrame original y el nombre de la sede o el dict de horarios
# -------------------------
def procesar_registros(df, sede_or_horario):
    """
    Procesa marcaciones y genera reporte con:
    Nombre, Fecha, Día, Entrada, Salida, Horas trabajadas, Tardanza, Horas extras(Horas y minutos)
    """

    


    df = df.copy()
    df.columns = [c.strip() for c in df.columns]


    # Normalizar nombres a minúsculas sin espacios
    df.columns = df.columns.str.strip().str.lower()

    # Mapeo fijo y sencillo
    df = df.rename(columns={
        "nombre": "nombre",
        "name": "nombre",
        "user name": "nombre",

        "fecha_hora": "fecha_hora",
        "hora": "fecha_hora",
        "time": "fecha_hora",
        "date/time": "fecha_hora",
        "datetime": "fecha_hora",
        "check-in/out": "fecha_hora",
    }, errors="ignore")

    # Verificar que existan las 2 columnas mínimas
    if "nombre" not in df.columns or "fecha_hora" not in df.columns:
        raise ValueError(f"Faltan columnas requeridas. Columnas actuales: {df.columns.tolist()}")


    df["__fecha_dt"] = pd.to_datetime(df["fecha_hora"], errors="coerce")
    

    col_nombre, col_fecha = detectar_columnas(df)
    if not col_nombre or not col_fecha:
        raise ValueError(f"No se pudieron detectar columnas de nombre/fecha. Columnas: {list(df.columns)}")

    df = df.rename(columns={col_nombre: "nombre", col_fecha: "fecha_hora"})

    df["__fecha_dt"] = pd.to_datetime(df["fecha_hora"], errors="coerce")

    df = df.dropna(subset=["__fecha_dt"])
    df["fecha"] = df["__fecha_dt"].dt.date
    df["hora"] = df["__fecha_dt"].dt.time




    resumen = (
        df.groupby(["nombre", "fecha"])
          .agg(hora_entrada=("hora", "min"),
               hora_salida=("hora", "max"),
               marcas_count=("hora", "count"))
          .reset_index()
    )

    filas_result = []

    if isinstance(sede_or_horario, str):
        horario_por_dia = HORARIOS_SEDES[sede_or_horario]
    else:
        horario_por_dia = sede_or_horario

    for _, row in resumen.iterrows():
        nombre = row["nombre"]
        fecha = row["fecha"]
        entrada = row["hora_entrada"]
        salida = row["hora_salida"]
        marcas = row["marcas_count"]

        dia_ing = datetime.strptime(str(fecha), "%Y-%m-%d").strftime("%A")
        dia_es = DIAS_MAP.get(dia_ing, dia_ing)

        if dia_es == "Domingo":
            continue

        horario_dia = horario_por_dia.get(dia_es)
        if not horario_dia:
            continue

        # ============================
        # 🚨 CASO 1: NO MARCÓ NADA
        # ============================
        if pd.isna(entrada) and pd.isna(salida):
            filas_result.append({
                "Nombre": nombre,
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Día": dia_es,
                "Entrada": "-:--",
                "Salida": "-:--",
                "Horas trabajadas": "no marcó entrada ni salida",
                "Tardanza": "no marcó",
                "Horas extras": "no marcó"
            })
            continue

               # ============================
        # 🚨 CASO 2: SOLO UNA MARCACIÓN
        # ============================
        if marcas == 1:
            hora_unica = entrada  # (entrada == salida cuando marcas=1)

            # Rango oficial
            entrada_ini = datetime.strptime("08:00", "%H:%M").time()
            entrada_fin = datetime.strptime("13:30", "%H:%M").time()
            salida_ini  = datetime.strptime("13:31", "%H:%M").time()
            salida_fin  = datetime.strptime("17:00", "%H:%M").time()

            # --- Clasificación por rango ---
            if entrada_ini <= hora_unica <= entrada_fin:
                # Es ENTRADA
                entrada_str = hora_unica.strftime("%H:%M")

                salida_str = "--:--"
                salida_str = "-:--"

                msg = "no marcó salida"

            elif salida_ini <= hora_unica <= salida_fin:
                # Es SALIDA

                entrada_str = "--:--"

                entrada_str = "-:--"

                salida_str = hora_unica.strftime("%H:%M")
                msg = "no marcó entrada"

            else:
                # --- Hora fuera de rango → se decide por cercanía ---
                td_unica = timedelta(hours=hora_unica.hour, minutes=hora_unica.minute)
                td_entrada_ref = timedelta(hours=entrada_ini.hour, minutes=entrada_ini.minute)
                td_salida_ref = timedelta(hours=salida_fin.hour, minutes=salida_fin.minute)

                if abs(td_unica - td_entrada_ref) <= abs(td_unica - td_salida_ref):
                    # Más cerca de entrada
                    entrada_str = hora_unica.strftime("%H:%M")

                    salida_str = "--:--"
                    msg = "no marcó salida"
                else:
                    # Más cerca de salida
                    entrada_str = "--:--"

                    salida_str = "-:--"
                    msg = "no marcó salida"
                else:
                    # Más cerca de salida
                    entrada_str = "-:--"

                    salida_str = hora_unica.strftime("%H:%M")
                    msg = "no marcó entrada"

            filas_result.append({
                "Nombre": nombre,
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Día": dia_es,
                "Entrada": entrada_str,
                "Salida": salida_str,
                "Horas trabajadas": msg,
                "Tardanza": msg,
                "Horas extras": msg
            })
            continue


        # ============================
        # 🚨 CASO 3: FALTA UNA MARCACIÓN AUNQUE MARCAS>=2
        # (Extremadamente raro pero lo cubrimos)
        # ============================
        if pd.isna(entrada):
            filas_result.append({
                "Nombre": nombre,
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Día": dia_es,
                "Entrada": "-:--",
                "Salida": salida.strftime("%H:%M"),
                "Horas trabajadas": "no marcó entrada",
                "Tardanza": "no marcó entrada",
                "Horas extras": "no marcó entrada"
            })
            continue

        if pd.isna(salida):
            filas_result.append({
                "Nombre": nombre,
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Día": dia_es,
                "Entrada": entrada.strftime("%H:%M"),
                "Salida": "-:--",
                "Horas trabajadas": "no marcó salida",
                "Tardanza": "no marcó salida",
                "Horas extras": "no marcó salida"
            })
            continue

        # ✔️ CASO NORMAL: ENTRADA Y SALIDA OK
        entrada_dt = datetime.combine(fecha, entrada)
        salida_dt = datetime.combine(fecha, salida)

        entrada_oficial = datetime.combine(fecha, datetime.strptime(horario_dia["entrada"], "%H:%M").time())
        salida_oficial = datetime.combine(fecha, datetime.strptime(horario_dia["salida"], "%H:%M").time())

        tardanza = entrada_dt - entrada_oficial
        if tardanza < timedelta(0):
            tardanza = timedelta(0)


        # ================================
# ⚡ CORRECCIÓN: Descuento de almuerzo
# ================================
        SEDE_NO_ALMUERZO = "barranquilla"   # 👉 cambia por el nombre exacto de esa sede

        horas_trab = salida_dt - entrada_dt

        # Si **NO es** la sede especial -> descontar almuerzo normal
        if sede_or_horario != SEDE_NO_ALMUERZO:
            horas_trab -= timedelta(hours=1)

        # Si sí es la sede especial -> SOLO descontar si NO es sábado
        else:
            if dia_es != "Sábado":   # sábado NO descuenta
                horas_trab -= timedelta(hours=1)

        # Evitar negativos
        if horas_trab < timedelta(0):
            horas_trab = timedelta(0)


        horas_trab = salida_dt - entrada_dt - timedelta(hours=1)

        if horas_trab < timedelta(0):
            horas_trab = timedelta(0)

        # 🔥 Aquí aplicas tu nueva función de cálculo de extras
        extras_effect = calcular_extras(
        entrada_dt=entrada_dt,
        salida_dt=salida_dt,
        entrada_oficial_dt=entrada_oficial,
        salida_oficial_dt=salida_oficial,
        tardanza_td=tardanza
        )



            salida_dt=salida_dt,
            salida_oficial_dt=salida_oficial,
            tardanza_td=tardanza
        )


            "Nombre": nombre,
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Día": dia_es,
            "Entrada": entrada.strftime("%H:%M"),
            "Salida": salida.strftime("%H:%M"),
            "Horas trabajadas": formato_hhmm(horas_trab),
            "Tardanza": formato_hhmm(tardanza),
            "Horas extras": formato_hhmm(extras_effect)
        })

            # ==========================================================
    # 🔥 CALCULAR HORAS EXTRAS TOTALES POR PERSONA
    # ==========================================================
    

    df_resultado = pd.DataFrame(filas_result)

    print("COLUMNAS DF_RESULTADO:", df_resultado.columns.tolist())


# =======================================
# CALCULAR TOTAL DE HORAS EXTRAS POR PERSONA
# =======================================

    def extras_to_minutes(x):
        if isinstance(x, str) and "h" in x:
            partes = x.replace("h", "").replace("m", "").split()
            h = int(partes[0])
            m = int(partes[1])
            return h * 60 + m
        return 0

    # Convertir texto → minutos
    

    df_resultado["extras_min"] = df_resultado["Horas extras"].apply(extras_to_minutes)

    # Sumar minutos por persona
    totales = (
        df_resultado.groupby("Nombre")["extras_min"]
        .sum()
        .reset_index()
    )

    # Convertir de vuelta a formato "Hh Mm"
    totales["total_extras_hhmm"] = totales["extras_min"].apply(
        lambda m: f"{m//60:02d}h {m%60:02d}m"
    )

    # =======================================
    # INSERTAR FILA TOTAL DESPUÉS DE CADA PERSONA
    # =======================================

    filas_finales = []
    for nombre, grupo in df_resultado.groupby("Nombre"):
        # Agregar todas las filas de esa persona
        filas_finales.extend(grupo.drop(columns=["extras_min"]).to_dict("records"))

        # Buscar su total
        total_str = totales.loc[totales["Nombre"] == nombre, "total_extras_hhmm"].iloc[0]

        # Insertar fila total
        filas_finales.append({
            "Nombre": f"TOTAL HORAS EXTRAS ({nombre})",
            "Fecha": "",
            "Día": "",
            "Entrada": "",
            "Salida": "",
            "Horas trabajadas": "",
            "Tardanza": "",
            "Horas extras": total_str
        })

    # Convertir a DataFrame final ordenado
    df_final = pd.DataFrame(filas_finales)

    

   
    return df_final


        




    return pd.DataFrame(filas_result)

