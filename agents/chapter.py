"""Rol chapter: edita aquí sus instrucciones y entregables."""

import re

from graph.state import WorkflowState
from graph.context import _ctx, _runs, _const_block, _ronda, _feedback_block


INSTRUCTIONS = (
    "Eres el Chapter, responsable de la revisión técnica final del equipo. "
    "Usa el Issue y sus criterios de aceptación del contexto del proyecto como alcance. "
    "Si no están disponibles, indícalo y no inventes criterios. Contrasta cada criterio "
    "con arquitectura, persistencia cuando aplique, implementación, pruebas y seguridad. "
    "Revisa sólo las áreas incluidas en el tipo de proyecto; no marques como faltante "
    "un rol que no aplica. Si falta el informe de un rol aplicable, márcalo NO VERIFICABLE. "
    "Detecta contratos incompatibles, falta de cobertura y hallazgos pendientes. "
    "Devuelve el contenido de un informe chapter_report.md con estas secciones: "
    "Resumen; Matriz de criterios (ID CA-01, CA-02..., criterio, evidencia y origen, "
    "estado CUMPLIDO/PENDIENTE/NO VERIFICABLE y verificación); Incompatibilidades y "
    "hallazgos; Observaciones por corregir (ID OBS-01..., severidad BLOQUEANTE/ALTA/"
    "MEDIA/BAJA, responsable, cambio requerido y cómo verificarlo); Seguimiento de "
    "observaciones previas (mismo ID, estado CORREGIDA/PARCIAL/PENDIENTE y evidencia); "
    "Pruebas pendientes; Aprobaciones humanas; y Veredicto. Mantén los IDs de los "
    "criterios y observaciones entre rondas. Asigna IDs CA según el orden del Issue y "
    "IDs OBS consecutivos; conserva los IDs "
    "previos aunque una observación siga abierta. Cierra una observación como CORREGIDA "
    "sólo si evidencia actual demuestra la corrección; si el feedback previo contradice "
    "los informes actuales o la evidencia es incompleta, márcala PARCIAL/PENDIENTE y "
    "explica la discrepancia. Cita sólo evidencia presente en los informes, como "
    "rutas, contratos, casos de prueba o resultados reportados. Sólo afirma que el "
    "código o una prueba fue verificado si el material recibido contiene esa evidencia; "
    "distingue propuestas de pruebas ejecutadas y marca NO EJECUTADO lo que no tenga "
    "resultado comprobable. Nunca inventes ejecuciones, resultados, criterios ni "
    "aprobaciones. El estado no contiene una señal estructurada de aprobación humana: "
    "no infieras ni sustituyas esas aprobaciones; indica NO INDICADA si no hay evidencia "
    "explícita. Registra aprobaciones humanas aparte del veredicto técnico; su ausencia "
    "no equivale a aprobación ni a rechazo humano. Reenvía a desarrollo las "
    "observaciones pendientes o parciales con su ID, responsable, cambio y comprobación. "
    "Emite en una línea independiente "
    "exactamente `VEREDICTO: APROBADO`, `VEREDICTO: APROBADO CON OBSERVACIONES` o "
    "`VEREDICTO: RECHAZADO`. Usa APROBADO sólo si se conocen los criterios aplicables, "
    "todos están CUMPLIDOS con evidencia suficiente y no quedan observaciones técnicas "
    "pendientes. Usa APROBADO CON OBSERVACIONES si faltan criterios, hay criterios "
    "PENDIENTES/NO VERIFICABLES, brechas corregibles o pruebas relevantes pendientes; "
    "las pruebas opcionales o ajenas al Issue no impiden aprobar, pero explica su "
    "exclusión. Usa RECHAZADO sólo ante un incumplimiento confirmado y respaldado por "
    "evidencia que impida un criterio central, cause pérdida/corrupción de datos, permita "
    "acceso no autorizado a datos sensibles/acciones críticas, o haga imposible integrar "
    "contratos necesarios. Un riesgo ALTO no es automáticamente bloqueante: justifica "
    "por qué cumple o no esa definición. No conviertas falta de evidencia en "
    "incumplimiento confirmado: clasifícala como NO VERIFICABLE y usa observaciones.\n"
)


def chapter_node(state: WorkflowState, invoke) -> dict:
    """
    Revisa los cambios y emite veredicto. Si deja observaciones, quedan en
    `review_feedback` para que el dev las incorpore en la ronda siguiente.

    Usa `context` como checklist de compliance.
    Escribe en: out_chapter, review_feedback, last_verdict, approved, review_round
    """
    ronda = _ronda(state)  # esta revision incrementa el contador
    print(f"[chapter_node] Revisando cambios (ronda {ronda})...")

    report_fields = [
        ("out_architect", "Arquitectura"),
        ("out_analysis", "Análisis del repositorio"),
        ("out_plan", "Plan del equipo"),
    ]
    if _runs(state, "backend"):
        report_fields.append(("out_backend", "Backend"))
    if _runs(state, "frontend"):
        report_fields.append(("out_frontend", "Frontend"))
    report_fields.extend(
        (("out_testing", "Pruebas"), ("out_security", "Seguridad"))
    )
    reports = "\n\n".join(
        f"## {label}\n{_ctx(state.get(field, '') or 'NO DISPONIBLE', 6000)}"
        for field, label in report_fields
    )

    prompt = (
        INSTRUCTIONS
        + _const_block(state, "Respeta el alcance del Issue y la constitución.")
        + "\nRepositorio: "
        + state["repo_name"]
        + "\nRonda de revisión: "
        + str(ronda)
        + "\nTipo de proyecto: "
        + state.get("project_type", "ambos")
        + "\nIssue y criterios de aceptación: usa los que aparecen en el contexto "
        "del proyecto. Si no aparecen, informa que no están disponibles y no inventes "
        "una lista de criterios."
        + "\nInformes del equipo:\n"
        + reports
        + _feedback_block(state)
    )
    if state.get("include_data"):
        prompt += (
            "\nDatos y persistencia (área aplicable): revisa tablas, relaciones, "
            "restricciones y migraciones. Informe:\n"
            + _ctx(state.get("out_data", "") or "NO DISPONIBLE", 6000)
        )
    else:
        prompt += (
            "\nDatos y persistencia: no hay un informe separado de Datos. Determina "
            "si aplica al Issue; revisa la evidencia disponible en arquitectura y "
            "backend, y señala cualquier aspecto aplicable que no pueda verificarse."
        )
    salida = invoke(prompt)
    veredicto = parse_verdict(salida)

    etiqueta = {
        "aprobado": "APROBADO ✓",
        "observaciones": "APROBADO CON OBSERVACIONES",
        "rechazado": "RECHAZADO ✗",
    }[veredicto]
    print(f"[chapter_node] Ronda {ronda}: {etiqueta}")

    return {
        "out_chapter": salida,
        "review_feedback": salida,  # lo lee el dev en la ronda siguiente
        "last_verdict": veredicto,
        "approved": veredicto == "aprobado",
        "review_round": ronda,
    }


def parse_verdict(text: str) -> str:
    """
    Interpreta una única línea de veredicto explícita; ambigüedad fuerza otra ronda.

    Retorna: "aprobado" | "observaciones" | "rechazado"
    """
    lines = [
        line.strip()
        for line in (text or "").splitlines()
        if re.match(r"^\s*VEREDICTO\b", line, flags=re.IGNORECASE)
    ]
    if len(lines) != 1:
        return "observaciones"

    match = re.fullmatch(
        r"VEREDICTO:\s*(APROBADO CON OBSERVACIONES|APROBADO|RECHAZADO)",
        lines[0],
        flags=re.IGNORECASE,
    )
    if not match:
        return "observaciones"
    result = match.group(1).upper()
    if result == "APROBADO CON OBSERVACIONES":
        return "observaciones"
    if result == "RECHAZADO":
        return "rechazado"
    return "aprobado"
