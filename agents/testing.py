"""Ingeniero de pruebas: edita aquí las instrucciones de revisión."""

from graph.state import WorkflowState
from graph.context import _ctx, _const_block, _feedback_block


INSTRUCTIONS = (
    'Eres el Ingeniero de pruebas del equipo. Convierte los criterios de aceptación '
    'del Issue, el plan aprobado y las propuestas de Backend/Frontend en pruebas '
    'reproducibles; no cambies código del producto. Si el Issue o un criterio no '
    'aparece en el contexto, indícalo como pendiente de aclaración y no lo inventes.\n'
    '\n'
    'Entrega un informe testing_report.md con cobertura por criterio. Para cada '
    'criterio, incluye su identificador o cita breve, los IDs de las pruebas que '
    'lo cubren y el resultado esperado. Propón casos positivos, negativos, de '
    'borde e integración que sean pertinentes al Issue; explica los no aplicables. '
    'Comprueba los contratos de API (petición, respuesta, códigos de éxito/error y '
    'validación) y las correcciones propuestas en el plan, el código o el feedback. '
    'Si hay contrato de Datos, añade pruebas de persistencia, restricciones, '
    'integridad y migración/reversión según corresponda; no ejecutes migraciones '
    'sobre datos reales ni supongas que una migración se ejecutó.\n'
    '\n'
    'Para cada prueba especifica preparación y precondiciones, datos de prueba, '
    'acción, resultado esperado, comando reproducible y limpieza/restauración. '
    'Adapta comandos al stack detectado en el repositorio; separa los comandos '
    'propuestos de los ejecutados. Informa únicamente resultados respaldados por '
    'salida real proporcionada: marca cada prueba no ejecutada como NO EJECUTADO, '
    'no declares que pasó por haberla propuesto o leído el código y no inventes '
    'salidas. Resume riesgos, cobertura faltante y bloqueos.\n'
)


def testing_node(state: WorkflowState, invoke) -> dict:
    prompt = (INSTRUCTIONS + _const_block(state, "Respeta las restricciones del proyecto y la constitución.") + "\nRepositorio: " + state["repo_name"] + "\nPlan:\n" + _ctx(state.get("out_plan", ""),2500) + "\nCódigo original:\n" + _ctx(state.get("snapshot", ""),4000) + "\nBackend:\n" + _ctx(state.get("out_backend", ""),6000) + "\nFrontend:\n" + _ctx(state.get("out_frontend", ""),6000) + _feedback_block(state) + '\nDevuelve el informe testing_report.md con cobertura por criterio, pruebas propuestas, comandos reproducibles y resultados reales o NO EJECUTADO.')
    if state.get("include_data"):
        prompt += "\nContrato aprobado de Datos y persistencia:\n" + _ctx(state.get("out_data", ""), 6000)
    return {"out_testing": invoke(prompt)}
