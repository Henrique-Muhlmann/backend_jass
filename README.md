# BACK-END JASS 

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![Status](https://img.shields.io/badge/status-online-brightgreen)

Sistema modular de back-end para plataforma robótica com coleta, processamento e exposição de dados em tempo real. Desenvolvido com Python, FastAPI e programação assíncrona.

## Índice

- [Visão Geral](#visão-geral)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura de Dados](#estrutura-de-dados)
- [Arquivos Gerados](#arquivos-gerados)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Integração com Hardware Real](#integração-com-hardware-real)
- [Troubleshooting](#troubleshooting)

## Visão Geral

Este sistema foi projetado para coletar, processar e disponibilizar dados de sensores robóticos através de uma API REST. O sistema simula a coleta de dados de hardware (motores, pallets e giroscópio) a cada 2 segundos, processa e persiste os dados em dois formatos:

- **Dados Atuais**: Última coleta (substituição)
- **Histórico**: Acumulação de todas as coletas com timestamps

## Características

### Funcionalidades Principais

- **Coleta em Tempo Real**: Simulação de coleta de dados a cada 2 segundos
- **Processamento Assíncrono**: Não bloqueia a API durante o processamento
- **Persistência Dual**: 
  - Dados atuais para monitoramento em tempo real
  - Histórico completo para análise e Machine Learning
- **API RESTful**: Endpoints documentados com FastAPI
- **Validação de Dados**: Tipagem forte com Pydantic
- **Modularidade**: Código organizado em módulos independentes
- **Singleton Pattern**: Gerenciamento centralizado de estado

### Recursos Técnicos

- Python 3.10+
- FastAPI para API REST
- Pydantic para validação de dados
- Programação assíncrona (asyncio)
- Persistência em JSON
- Documentação interativa automática (Swagger/OpenAPI)

## Arquitetura

### Módulos Principais

```
Sistema Back-end Robótico
│
├── DataModels
│   ├── RawMotorData
│   ├── RawPalletData
│   ├── RawCentroidData
│   ├── ProcessedMotor
│   ├── ProcessedPallet
│   ├── Giroscopio
│   ├── ProcessedRobotData
│   └── HistoricalRecord
│
├── DataSimulator
│   └── Simulação de dados do hardware
│
├── DataProcessor
│   └── Transformação e renomeação de variáveis
│
├── DataManager (Singleton)
│   ├── Gerenciamento de estado
│   ├── Persistência em disco
│   └── Controle de histórico
│
├── BackgroundTaskManager
│   └── Loop assíncrono de atualização
│
└── FastAPI Application
    ├── GET /api/data
    ├── GET /api/hist_data
    └── GET /docs
```

## Requisitos

### Software

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Dependências Python

```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
```

## Instalação

### 1. Clone ou baixe o projeto

```bash
# Crie um diretório para o projeto
mkdir robot-backend
cd robot-backend
```

### 2. Instale as dependências

```bash
pip install fastapi uvicorn pydantic
```

### 3. Salve o código principal

Salve o código fornecido em um arquivo chamado `main.py`

### 4. Estrutura de diretórios

O sistema criará automaticamente o diretório `data/` quando executado pela primeira vez.

```
robot-backend/
│
├── main.py                 # Código principal
└── data/                   # Criado automaticamente
    ├── robot_data.json     # Dados atuais
    └── hist_data.json      # Histórico
```

## Uso

### Iniciar o servidor

```bash
python main.py
```

### Saída esperada

```
============================================================
INICIANDO SERVIDOR FASTAPI
============================================================
URL: http://localhost:8000
API de Dados Atuais: http://localhost:8000/api/data
API de Histórico: http://localhost:8000/api/hist_data
Documentação: http://localhost:8000/docs
============================================================

============================================================
SISTEMA ROBÓTICO - INICIANDO
============================================================
[INFO] Dados atualizados em 2025-10-14 15:30:00
[INFO] Dados atuais salvos em data/robot_data.json
[INFO] Histórico salvo: 1 registros em data/hist_data.json
[INFO] Iniciando loop de atualização de dados (intervalo: 2s)
```

### Parar o servidor

Pressione `Ctrl + C` no terminal

## Endpoints da API

### 1. Dados Atuais

**Endpoint**: `GET http://localhost:8000/api/data`

**Descrição**: Retorna apenas a última coleta de dados (sempre atualizado)

**Exemplo de Resposta**:
```json
{
  "motors": [
    {
      "id": 1,
      "velocity": 142.3,
      "distance": 20.5,
      "temperature": 71.2
    },
    {
      "id": 2,
      "velocity": 138.9,
      "distance": 15.3,
      "temperature": 69.4
    },
    {
      "id": 3,
      "velocity": 155.0,
      "distance": 25.8,
      "temperature": 75.1
    }
  ],
  "pallets": [
    {
      "id": 12,
      "timestamp": "2025-10-14T15:30:00Z"
    }
  ],
  "giroscopio": {
    "centroid": {
      "x": 0.24,
      "y": -0.12,
      "z": 0.93
    }
  }
}
```

### 2. Histórico Completo

**Endpoint**: `GET http://localhost:8000/api/hist_data`

**Descrição**: Retorna todos os registros históricos com timestamps de coleta

**Exemplo de Resposta**:
```json
[
  {
    "timestamp_coleta": "2025-10-14T15:30:00Z",
    "data": {
      "motors": [...],
      "pallets": [...],
      "giroscopio": {...}
    }
  },
  {
    "timestamp_coleta": "2025-10-14T15:30:02Z",
    "data": {
      "motors": [...],
      "pallets": [...],
      "giroscopio": {...}
    }
  }
]
```

### 3. Documentação Interativa

**Endpoint**: `GET http://localhost:8000/docs`

**Descrição**: Interface Swagger para testar os endpoints interativamente

### 4. Informações do Sistema

**Endpoint**: `GET http://localhost:8000/`

**Descrição**: Informações básicas sobre a API e endpoints disponíveis

## Estrutura de Dados

### Dados Brutos (Hardware)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Motor.id | int | ID do motor (1, 2 ou 3) |
| Motor.velocity | float | Velocidade em RPM |
| Motor.cm | float | Distância em centímetros |
| Motor.temperature | float | Temperatura em Celsius |
| Pallet.id_pallet | int | ID do pallet |
| Pallet.timestamp_raw | string | Timestamp da coleta |
| Centroid.centroid_x | float | Coordenada X |
| Centroid.centroid_y | float | Coordenada Y |
| Centroid.centroid_z | float | Coordenada Z |

### Transformações Aplicadas

O sistema renomeia automaticamente as variáveis:

| Origem | Destino |
|--------|---------|
| `cm` | `distance` |
| `id_pallet` | `id` |
| `timestamp_raw` | `timestamp` |
| `centroid_x, centroid_y, centroid_z` | `giroscopio.centroid.{x,y,z}` |

### Ranges de Valores Simulados

| Variável | Range |
|----------|-------|
| velocity | 130.0 - 160.0 RPM |
| distance | 10.0 - 30.0 cm |
| temperature | 65.0 - 80.0 °C |
| id_pallet | 1 - 100 |
| centroid (x,y,z) | -1.0 - 1.0 |

## Arquivos Gerados

### data/robot_data.json

Contém apenas a última coleta. Este arquivo é **substituído** a cada atualização.

**Uso recomendado**: Monitoramento em tempo real, dashboards, visualizações ao vivo

### data/hist_data.json

Contém o histórico completo de todas as coletas desde o início da execução.

**Uso recomendado**: Treinamento de modelos de Machine Learning, análise histórica, relatórios

**Estrutura**:
```json
[
  {
    "timestamp_coleta": "ISO 8601 timestamp",
    "data": { /* dados processados */ }
  }
]
```

## Estrutura do Projeto

### Organização do Código

```python
# 1. DATA MODELS
# Definição de todos os modelos Pydantic

# 2. DATA SIMULATOR
# Lógica de simulação de dados do hardware

# 3. DATA PROCESSOR
# Transformação e renomeação de variáveis

# 4. DATA MANAGER
# Gerenciamento de estado e persistência (Singleton)

# 5. BACKGROUND TASKS
# Tarefas assíncronas em background

# 6. API SERVER
# Aplicação FastAPI e endpoints
```

### Padrões de Design Utilizados

- **Singleton**: DataManager (instância única)
- **Strategy**: DataSimulator e DataProcessor (intercambiáveis)
- **Repository**: DataManager (abstração de persistência)
- **Async/Await**: BackgroundTaskManager (não bloqueante)

## Integração com Hardware Real

### Substituindo o Simulador

Para integrar com hardware real, substitua o `DataSimulator` por uma classe que leia dados reais:

```python
class RealHardwareDataSource:
    """Classe para ler dados de hardware real"""
    
    @classmethod
    def read_hardware_data(cls) -> RawHardwareData:
        """
        Lê dados dos sensores reais
        Implemente a lógica de leitura aqui
        """
        # Exemplo: Leitura via serial, I2C, SPI, etc.
        motors = cls._read_motors()
        pallet = cls._read_pallet()
        centroid = cls._read_centroid()
        
        return RawHardwareData(
            motors=motors,
            pallet=pallet,
            centroid=centroid
        )
```


### Porta 8000 já em uso

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Ou altere a porta no código:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Erro ao instalar dependências

```bash
# Use um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstale as dependências
pip install --upgrade pip
pip install fastapi uvicorn pydantic
```

### Permissões de escrita (data/)

Certifique-se de que o usuário tem permissão de escrita no diretório:

```bash
chmod -R 755 data/  # Linux/Mac
```

### Logs não aparecem

Aumente o nível de log:

```python
uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
```

## Testes

### Testar endpoints com curl

```bash
# Dados atuais
curl http://localhost:8000/api/data

# Histórico
curl http://localhost:8000/api/hist_data

# Informações do sistema
curl http://localhost:8000/
```

### Testar com Python

```python
import requests

# Dados atuais
response = requests.get("http://localhost:8000/api/data")
print(response.json())

# Histórico
response = requests.get("http://localhost:8000/api/hist_data")
print(f"Total de registros: {len(response.json())}")
```

## Suporte

Para dúvidas ou problemas:
1. Consulte a documentação interativa em `/docs`
2. Verifique os logs no console

---

**Versão**: 1.0.0  
**Última atualização**: 14 Outubro 2025  
**Tecnologias**: Python 3.10+, FastAPI, Pydantic, Asyncio
