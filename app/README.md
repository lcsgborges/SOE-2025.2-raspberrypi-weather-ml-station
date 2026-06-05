# Application

Esta pasta concentra os componentes executáveis do projeto.

- `embedded/`: coletor C++ do BME280, servidor HTTP local e scripts de execução na Raspberry Pi.
- `web/`: dashboard servido pelo módulo embarcado.
- `runtime-data/`: CSV de leituras gerado em runtime.

O módulo embarcado deve ser executado a partir de `app/embedded`, pois os caminhos relativos apontam para `../web` e `../runtime-data`.
