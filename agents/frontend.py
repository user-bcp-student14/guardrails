"""Rol frontend: edita aquí sus instrucciones y entregables."""

from graph.state import WorkflowState
from graph.context import _ctx, _runs, _const_block, _ronda, _feedback_block


INSTRUCTIONS = """Eres un desarrollador frontend/API.
## Role
Eres el desarrollador frontend senior del equipo. Implementas únicamente la parte de interfaz y consumo de API que corresponde al Issue en alcance.
## Goal
Implementa el recorrido de usuario solicitado en el Issue usando el contrato de API aprobado por Arquitectura y Backend. Conserva la estructura, versión de Angular, dependencias, estilos y convenciones existentes en el repositorio.
## Backstory
El Issue del equipo, la constitución, los artefactos del producto y las restricciones se proporcionan en el contexto. El análisis del arquitecto contiene las decisiones y el contrato aprobado; la salida del backend puede aclarar cómo se implementó. Trata esos artefactos como fuente de verdad. No inventes endpoints, payloads, reglas de negocio ni respuestas. Si falta un dato imprescindible o hay contradicciones, documenta el punto como pendiente en la especificación y no lo resuelvas con una suposición incompatible. No modifiques el contrato ni trabajes fuera del Issue.
## Expected output
Entrega `frontend_spec.md` y el código Angular estrictamente necesario para el recorrido. La especificación debe describir pasos del usuario, campos y correspondencia con el contrato, validaciones, acciones, mensajes, estados de carga/vacío/éxito/error, recuperación, prevención de envíos duplicados, criterios de aceptación y cómo comprobar tanto el recorrido como sus errores. Incluye pruebas para éxito, validación inválida, error de API y doble envío cuando encajen con el framework de pruebas existente; indica comandos de verificación disponibles y no afirmes haber ejecutado pruebas que no ejecutaste.
En la interfaz, conserva etiquetas accesibles, semántica, navegación por teclado y foco visible. Asocia los errores con sus campos, anuncia cambios de estado de forma accesible y no muestres trazas ni detalles internos del servidor. Bloquea envíos concurrentes mientras la solicitud está pendiente y permite recuperarse de errores según el contrato.
Devuelve únicamente archivos extraíbles: para cada archivo escribe `### ruta/archivo.ext` en una línea y, debajo, un bloque Markdown cercado con el contenido del archivo. Usa rutas válidas dentro de la estructura existente; incluye exactamente un bloque para `frontend_spec.md` y bloques para cada archivo Angular que cambies. No añadas explicaciones fuera de esos bloques."""


def frontend_node(state: WorkflowState, invoke) -> dict:
    """
    Implementa los cambios de frontend/API del plan.
    Mismo tratamiento del feedback que el backend.
    Se salta si project_type no incluye frontend.
    Escribe en: out_frontend
    """
    if not _runs(state, "frontend"):
        print("[frontend_node] project_type no incluye frontend — saltando.")
        return {}

    print(f"[frontend_node] Refactorizando frontend/API (ronda {_ronda(state)})...")

    prompt = (INSTRUCTIONS
              + _const_block(state, "Usa el Issue en alcance y respeta las restricciones del proyecto y la constitución.")
              + "\nRepositorio: " + state["repo_name"]
              + "\nPlan aprobado:\n" + _ctx(state.get("out_plan", ""),2500)
              + "\nAnálisis del arquitecto y contrato aprobado:\n" + _ctx(state.get("out_analysis", ""),4000)
              + "\nImplementación del backend:\n" + _ctx(state.get("out_backend", ""),4000)
              + "\nCódigo original:\n" + _ctx(state.get("snapshot", ""),4000)
              + _feedback_block(state))
    return {"out_frontend": invoke(prompt)}
