# Experimento 1

Disponibilidad


## Objetivo

Validar si durante operación normal del sistema, y en presencia de fallas de comunicación la señal del botón de pánico es procesada por lo menos el 99.95% de las veces.

## Diseño

Visualización del experimento:

```mermaid
sequenceDiagram
  participant umon as Unidad de Monitoreo
  participant api as API Gateway
  participant gest as Gestión de Accionables
  umon->>api: Alerta
  loop [Reintentos]
    api->>gest: Alerta
    gest->>api: Alerta procesada
  end
  Note right of gest: Fallas sintéticas
  api->>umon: Alerta procesada
```

```mermaid
flowchart LR
  subgraph Cliente
    umon[Unidad de Monitoreo]
  end
  umon<-->api
  subgraph Servicios
    api[API Gateway]
    gest[Gestión de Accionables]
    api<-->gest
  end
```

## Descripción Tecnológica

Se utiliza docker para orquestar el levantamiento de los tres componentes.

1. API Gateway: nginx configurado para apuntar a los servicios internos.
2. Gestión de accionables: receptor de las acciones
3. Unidad de monitoreo: generador de acciones

## Instrucciones

Requerimientos: docker

1. `docker compose up --build`
2. Hacer http request de prueba: `curl http://127.0.0.1:8080/comandos/gestion_accionables/`
