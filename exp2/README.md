# Experimento 2

Seguridad


## Objetivo

Validar la autenticación de la plataforma, garantiza la confidencialidad y evita la suplantación con medidas de doble factor.

## Diseño

Escenario válido de autenticación:

```mermaid
sequenceDiagram
  participant cli as Cliente Web
  participant api as API Gateway
  participant gu as Gestión de Usuarios
  participant no as Notificador
  cli->>api: Solicitud de Autenticación
  api->>gu: Solicitud de Autenticación
  gu->>no: Solicitud de envío de token de doble factor
  gu->>api: Respuesta preguntando token de doble factor
  api->>cli: Respuesta preguntando token de doble factor
  no->>cli: Token de doble factor
  cli->>api: Enviando token
  api->>gu: Enviando token
  gu->>api: Respuesta con token autenticación
  api->>cli: Respuesta con token de autenticación
```

```mermaid
flowchart LR
  subgraph Cliente
    web[Cliente Web]
  end
  web<-->api
  subgraph Servicios
    api[API Gateway]
    gu[Gestión de Usuarios]
    no[Notificador]
    api<-->gu
    gu<-->no
  end
```

## Descripción Tecnológica

Se utiliza docker para orquestar el levantamiento de los cuatro componentes.

1. Cliente Web: quien intenta autenticarse
2. API Gateway: nginx configurado para apuntar a los servicios internos.
3. Gestión de Usuarios: receptor de las acciones
4. Notificador: entrega los token al cliente para que se valide
