"""
Sistema Back-end para Plataforma Robótica
Engenharia de Software Sênior - Python/FastAPI

Autor: Sistema de Back-end Robótico
Versão: 1.0.0
Descrição: Sistema modular para coleta, processamento e exposição de dados robóticos em tempo real
"""

import asyncio
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field


# ============================================================================
# MÓDULO: DATA MODELS (Definição de Estruturas de Dados)
# ============================================================================


class RawMotorData(BaseModel):
    """Modelo de dados brutos recebidos do motor (hardware)"""

    id: int = Field(..., description="ID único do motor")
    velocity: float = Field(..., description="Velocidade do motor em RPM")
    cm: float = Field(..., description="Distância em centímetros")
    temperature: float = Field(..., description="Temperatura em Celsius")


class RawPalletData(BaseModel):
    """Modelo de dados brutos recebidos do pallet (hardware)"""

    id_pallet: int = Field(..., description="ID único do pallet")
    timestamp_raw: str = Field(..., description="Timestamp de coleta")


class RawCentroidData(BaseModel):
    """Modelo de dados brutos do giroscópio (hardware)"""

    centroid_x: float = Field(..., description="Coordenada X do centróide")
    centroid_y: float = Field(..., description="Coordenada Y do centróide")
    centroid_z: float = Field(..., description="Coordenada Z do centróide")


class RawHardwareData(BaseModel):
    """Agregação de todos os dados brutos recebidos do hardware"""

    motors: List[RawMotorData]
    pallet: RawPalletData
    centroid: RawCentroidData


# --- Modelos Processados (Formato Final para ML) ---


class ProcessedMotor(BaseModel):
    """Modelo de motor processado (renomeado e formatado)"""

    id: int
    velocity: float
    distance: float  # Renomeado de 'cm'
    temperature: float


class ProcessedPallet(BaseModel):
    """Modelo de pallet processado (renomeado e formatado)"""

    id: int  # Renomeado de 'id_pallet'
    timestamp: str  # Renomeado de 'timestamp_raw'


class Centroid(BaseModel):
    """Modelo de centróide do giroscópio"""

    x: float
    y: float
    z: float


class Giroscopio(BaseModel):
    """Modelo de giroscópio com centróide aninhado"""

    centroid: Centroid


class ProcessedRobotData(BaseModel):
    """Modelo final de dados processados para ML e API"""

    motors: List[ProcessedMotor]
    pallets: List[ProcessedPallet]
    giroscopio: Giroscopio


class HistoricalRecord(BaseModel):
    """Modelo para registro histórico com timestamp de coleta"""

    timestamp_coleta: str
    data: ProcessedRobotData


# ============================================================================
# MÓDULO: DATA SIMULATOR (Simulação de Dados do Hardware)
# ============================================================================


class DataSimulator:
    """
    Responsável por simular dados brutos vindos do hardware robótico.
    Gera valores aleatórios realistas para testes e desenvolvimento.
    """

    @staticmethod
    def generate_motor_data(motor_id: int) -> RawMotorData:
        """
        Gera dados simulados para um motor específico

        Args:
            motor_id: ID do motor (1, 2 ou 3)

        Returns:
            RawMotorData com valores aleatórios realistas
        """
        return RawMotorData(
            id=motor_id,
            velocity=round(random.uniform(130.0, 160.0), 1),
            cm=round(random.uniform(10.0, 30.0), 1),
            temperature=round(random.uniform(65.0, 80.0), 1),
        )

    @staticmethod
    def generate_pallet_data() -> RawPalletData:
        """
        Gera dados simulados para um pallet

        Returns:
            RawPalletData com timestamp atual
        """
        return RawPalletData(
            id_pallet=random.randint(1, 100),
            timestamp_raw=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def generate_centroid_data() -> RawCentroidData:
        """
        Gera dados simulados para o giroscópio (centróide)

        Returns:
            RawCentroidData com coordenadas normalizadas
        """
        return RawCentroidData(
            centroid_x=round(random.uniform(-1.0, 1.0), 2),
            centroid_y=round(random.uniform(-1.0, 1.0), 2),
            centroid_z=round(random.uniform(-1.0, 1.0), 2),
        )

    @classmethod
    def simulate_hardware_data(cls) -> RawHardwareData:
        """
        Simula uma coleta completa de dados do hardware

        Returns:
            RawHardwareData contendo dados de todos os sensores
        """
        motors = [cls.generate_motor_data(i) for i in range(1, 4)]
        pallet = cls.generate_pallet_data()
        centroid = cls.generate_centroid_data()

        return RawHardwareData(motors=motors, pallet=pallet, centroid=centroid)


# ============================================================================
# MÓDULO: DATA PROCESSOR (Processamento e Transformação de Dados)
# ============================================================================


class DataProcessor:
    """
    Responsável por transformar dados brutos em formato processado.
    Realiza renomeação de variáveis e reestruturação para formato ML.
    """

    @staticmethod
    def process_motor(raw_motor: RawMotorData) -> ProcessedMotor:
        """
        Processa dados de um motor individual

        Args:
            raw_motor: Dados brutos do motor

        Returns:
            ProcessedMotor com variáveis renomeadas (cm -> distance)
        """
        return ProcessedMotor(
            id=raw_motor.id,
            velocity=raw_motor.velocity,
            distance=raw_motor.cm,  # Renomeação: cm -> distance
            temperature=raw_motor.temperature,
        )

    @staticmethod
    def process_pallet(raw_pallet: RawPalletData) -> ProcessedPallet:
        """
        Processa dados de um pallet

        Args:
            raw_pallet: Dados brutos do pallet

        Returns:
            ProcessedPallet com variáveis renomeadas (id_pallet -> id, timestamp_raw -> timestamp)
        """
        return ProcessedPallet(
            id=raw_pallet.id_pallet,  # Renomeação: id_pallet -> id
            timestamp=raw_pallet.timestamp_raw,  # Renomeação: timestamp_raw -> timestamp
        )

    @staticmethod
    def process_centroid(raw_centroid: RawCentroidData) -> Giroscopio:
        """
        Processa dados do giroscópio

        Args:
            raw_centroid: Dados brutos do centróide

        Returns:
            Giroscopio com estrutura aninhada {"centroid": {"x", "y", "z"}}
        """
        centroid = Centroid(
            x=raw_centroid.centroid_x,
            y=raw_centroid.centroid_y,
            z=raw_centroid.centroid_z,
        )
        return Giroscopio(centroid=centroid)

    @classmethod
    def process_hardware_data(cls, raw_data: RawHardwareData) -> ProcessedRobotData:
        """
        Processa todos os dados brutos do hardware

        Args:
            raw_data: Dados brutos completos do hardware

        Returns:
            ProcessedRobotData no formato final para ML
        """
        processed_motors = [cls.process_motor(motor) for motor in raw_data.motors]
        processed_pallet = cls.process_pallet(raw_data.pallet)
        processed_giroscopio = cls.process_centroid(raw_data.centroid)

        return ProcessedRobotData(
            motors=processed_motors,
            pallets=[processed_pallet],  # Lista com um elemento
            giroscopio=processed_giroscopio,
        )


# ============================================================================
# MÓDULO: DATA MANAGER (Gerenciamento de Estado e Persistência)
# ============================================================================


class DataManager:
    """
    Singleton responsável por gerenciar o estado atual dos dados,
    persistência em disco (dados atuais e histórico) e ciclo de atualização.
    """

    _instance: Optional["DataManager"] = None

    def __new__(cls):
        """Implementação do padrão Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa o gerenciador de dados"""
        if self._initialized:
            return

        self.current_data: Optional[ProcessedRobotData] = None
        self.historical_data: List[HistoricalRecord] = []

        # Caminhos dos arquivos
        self.data_path = Path("data/robot_data.json")
        self.hist_data_path = Path("data/hist_data.json")

        self.simulator = DataSimulator()
        self.processor = DataProcessor()
        self._initialized = True

        # Cria diretório se não existir
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        # Carrega dados existentes, se houver
        self._load_current_from_disk()
        self._load_historical_from_disk()

    def _load_current_from_disk(self):
        """Carrega dados atuais persistidos do disco (se existirem)"""
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data_dict = json.load(f)
                    self.current_data = ProcessedRobotData(**data_dict)
                    print(f"[INFO] Dados atuais carregados de {self.data_path}")
            except Exception as e:
                print(f"[AVISO] Erro ao carregar dados atuais do disco: {e}")

    def _load_historical_from_disk(self):
        """Carrega histórico de dados do disco (se existir)"""
        if self.hist_data_path.exists():
            try:
                with open(self.hist_data_path, "r", encoding="utf-8") as f:
                    hist_list = json.load(f)
                    self.historical_data = [
                        HistoricalRecord(**record) for record in hist_list
                    ]
                    print(
                        f"[INFO] Histórico carregado: {len(self.historical_data)} registros"
                    )
            except Exception as e:
                print(f"[AVISO] Erro ao carregar histórico do disco: {e}")

    def _save_current_to_disk(self):
        """Persiste dados atuais no disco (substitui o arquivo)"""
        if self.current_data is None:
            return

        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(
                    self.current_data.model_dump(), f, indent=2, ensure_ascii=False
                )
            print(f"[INFO] Dados atuais salvos em {self.data_path}")
        except Exception as e:
            print(f"[ERRO] Erro ao salvar dados atuais no disco: {e}")

    def _save_historical_to_disk(self):
        """Persiste histórico completo no disco"""
        try:
            with open(self.hist_data_path, "w", encoding="utf-8") as f:
                hist_dict_list = [
                    record.model_dump() for record in self.historical_data
                ]
                json.dump(hist_dict_list, f, indent=2, ensure_ascii=False)
            print(
                f"[INFO] Histórico salvo: {len(self.historical_data)} registros em {self.hist_data_path}"
            )
        except Exception as e:
            print(f"[ERRO] Erro ao salvar histórico no disco: {e}")

    def _add_to_historical(self, data: ProcessedRobotData):
        """
        Adiciona um registro ao histórico com timestamp de coleta

        Args:
            data: Dados processados para adicionar ao histórico
        """
        timestamp_coleta = datetime.now(timezone.utc).isoformat()
        record = HistoricalRecord(timestamp_coleta=timestamp_coleta, data=data)
        self.historical_data.append(record)

    def update_data(self):
        """
        Executa um ciclo completo de atualização:
        1. Simula coleta de dados do hardware
        2. Processa dados brutos
        3. Atualiza estado interno (substitui dados atuais)
        4. Adiciona ao histórico
        5. Persiste ambos os arquivos no disco
        """
        # Simula coleta de dados
        raw_data = self.simulator.simulate_hardware_data()

        # Processa dados
        processed_data = self.processor.process_hardware_data(raw_data)

        # Atualiza estado atual (substitui)
        self.current_data = processed_data

        # Adiciona ao histórico
        self._add_to_historical(processed_data)

        # Persiste dados atuais
        self._save_current_to_disk()

        # Persiste histórico
        self._save_historical_to_disk()

        print(
            f"[INFO] Dados atualizados em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def get_current_data(self) -> Optional[ProcessedRobotData]:
        """Retorna os dados atuais"""
        return self.current_data

    def get_historical_data(self) -> List[HistoricalRecord]:
        """Retorna o histórico completo de dados"""
        return self.historical_data


# ============================================================================
# MÓDULO: BACKGROUND TASKS (Tarefas Assíncronas em Background)
# ============================================================================


class BackgroundTaskManager:
    """Gerencia tarefas assíncronas em background"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.task: Optional[asyncio.Task] = None

    async def data_update_loop(self):
        """
        Loop infinito que atualiza dados a cada 2 segundos
        Simula coleta em tempo real do hardware
        """
        print("[INFO] Iniciando loop de atualização de dados (intervalo: 2s)")

        while True:
            try:
                # Atualiza dados
                self.data_manager.update_data()

                # Aguarda 2 segundos
                await asyncio.sleep(2)

            except Exception as e:
                print(f"[ERRO] Erro no loop de atualização: {e}")
                await asyncio.sleep(2)  # Continua executando mesmo com erro

    async def start(self):
        """Inicia a tarefa em background"""
        self.task = asyncio.create_task(self.data_update_loop())

    async def stop(self):
        """Para a tarefa em background"""
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            print("[INFO] Loop de atualização encerrado")


# ============================================================================
# MÓDULO: API SERVER (FastAPI Application)
# ============================================================================

# Gerenciadores globais
data_manager = DataManager()
background_manager = BackgroundTaskManager(data_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    Inicia tarefas em background no startup e as encerra no shutdown
    """
    # Startup
    print("=" * 60)
    print("SISTEMA ROBÓTICO - INICIANDO")
    print("=" * 60)

    # Primeira atualização de dados
    data_manager.update_data()

    # Inicia loop de atualização em background
    await background_manager.start()

    yield

    # Shutdown
    print("\n" + "=" * 60)
    print("SISTEMA ROBÓTICO - ENCERRANDO")
    print("=" * 60)
    await background_manager.stop()


# Cria aplicação FastAPI
app = FastAPI(
    title="Sistema Back-end Robótico",
    description="API para coleta e processamento de dados robóticos em tempo real",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/data", response_model=ProcessedRobotData)
async def get_robot_data():
    """
    Endpoint para dados atuais: Retorna apenas a última coleta (substituição)

    Returns:
        ProcessedRobotData: Dados processados atuais dos motores, pallets e giroscópio
    """
    current_data = data_manager.get_current_data()

    if current_data is None:
        # Caso não haja dados, faz uma atualização imediata
        data_manager.update_data()
        current_data = data_manager.get_current_data()

    return current_data


@app.get("/api/hist_data", response_model=List[HistoricalRecord])
async def get_historical_data():
    """
    Endpoint para histórico: Retorna todos os registros históricos

    Returns:
        List[HistoricalRecord]: Lista completa do histórico com timestamps de coleta
    """
    historical_data = data_manager.get_historical_data()
    return historical_data


@app.get("/")
async def root():
    """Endpoint raiz com informações sobre a API"""
    return {
        "message": "Sistema Back-end Robótico",
        "version": "1.0.0",
        "endpoints": {
            "data": "/api/data - Dados robóticos atuais (última coleta)",
            "historical": "/api/hist_data - Histórico completo de dados",
            "docs": "/docs - Documentação interativa da API",
        },
        "status": "online",
    }


# ============================================================================
# EXECUÇÃO DA APLICAÇÃO
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("INICIANDO SERVIDOR FASTAPI")
    print("=" * 60)
    print("URL: http://localhost:8000")
    print("API de Dados Atuais: http://localhost:8000/api/data")
    print("API de Histórico: http://localhost:8000/api/hist_data")
    print("Documentação: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
