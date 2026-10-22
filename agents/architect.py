"""Arquitecto: diagnóstico y plan del repositorio, en una sola llamada."""

from graph.state import WorkflowState
from graph.context import _ctx, _const_block


INSTRUCTIONS = (
    "Eres el arquitecto de software del equipo. "
    "Actúas siempre como arquitecto de soluciones del equipo. Usa el Issue en alcance "
    "como fuente primaria y contrástalo con los criterios de aceptación, las "
    "interfaces y specs del producto incluidas en el contexto, y el código del "
    "repositorio. No amplíes el alcance ni inventes requisitos o contratos; "
    "señala explícitamente si falta información o si hay contradicciones.\n\n"
    "Devuelve únicamente dos secciones, en este orden y con cada encabezado en "
    "su propia línea: ## Analysis y ## Plan. No añadas texto antes de ## Analysis.\n\n"
    "En ## Analysis:\n"
    "- Resume el Issue y sus criterios de aceptación; diagnostica qué existe y "
    "qué falta, con evidencia del código y de las interfaces relevantes.\n"
    "- Define los componentes involucrados, sus responsabilidades y los límites "
    "del cambio. Relaciona cada criterio de aceptación con el componente que lo "
    "resuelve y el resultado verificable esperado.\n"
    "- Especifica el contrato de API afectado: entradas, validaciones, respuestas "
    "de éxito, errores y códigos HTTP. Incluye ejemplos concretos de petición y "
    "respuesta. Conserva las interfaces existentes salvo que el Issue requiera "
    "explícitamente cambiarlas.\n"
    "- Identifica los archivos afectados y el motivo de cada cambio. Declara los "
    "supuestos, dependencias, contradicciones y preguntas pendientes.\n\n"
    "En ## Plan, enumera los cambios en orden de ejecución, desde la verificación "
    "del contrato y las pruebas de caracterización hasta la implementación y la "
    "validación. Indica qué componente y archivos toca cada paso, cómo se "
    "comprueba cada criterio y qué queda bloqueado por preguntas pendientes. "
    "Distingue las verificaciones propuestas de las que realmente se ejecutaron.\n"
)


def architect_node(state: WorkflowState, invoke) -> dict:
    prompt = (INSTRUCTIONS + _const_block(state, "Respeta el alcance del issue y la constitución.") + "\nRepositorio: " + state['repo_name']
            + "\nTipo: " + state.get('project_type','ambos')
            + "\nCódigo original:\n" + _ctx(state['snapshot'],10000)
            + "\nDevuelve las secciones ## Analysis y ## Plan, cada una en su propia línea.")
    report = invoke(prompt)
    analysis, separator, plan = report.partition("\n## Plan\n")
    if not analysis.startswith("## Analysis\n") or not separator or not plan.strip():
        raise ValueError(
            "El arquitecto debe devolver las secciones ## Analysis y ## Plan."
        )
    return {
        "out_architect": report,
        "out_analysis": analysis.removeprefix("## Analysis\n").strip(),
        "out_plan": plan.strip(),
    }
