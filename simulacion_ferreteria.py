"""
Simulación Evento a Evento - Ferretería JYL
Implementación del algoritmo basado en diagramas de flujo

Evalúa diferentes configuraciones de empleados para minimizar tiempos de espera
"""

import numpy as np
import pandas as pd
import csv
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class EstadisticasCorrida:
    """Estadísticas de una corrida de simulación"""
    tiempo_promedio_permanencia: float
    tiempo_maximo_espera: float
    tiempo_promedio_atencion: float
    clientes_atendidos_total: int
    clientes_se_fueron: int  # Por arrepentimiento
    servidor_1_clientes: int
    servidor_2_clientes: int = 0
    servidor_3_clientes: int = 0

class SimuladorFerreteria:
    def __init__(self, numeros_pseudoaleatorios: List[float]):
        """
        Inicializa el simulador con números pseudoaleatorios validados.
        
        Args:
            numeros_pseudoaleatorios: Lista de números [0,1) que pasaron pruebas
        """
        self.numeros = numeros_pseudoaleatorios
        self.indice_numero = 0
        
    def obtener_numero_aleatorio(self) -> float:
        """Obtiene el siguiente número pseudoaleatorio de la secuencia validada"""
        if self.indice_numero >= len(self.numeros):
            self.indice_numero = 0  # Reiniciar si se agotan
        
        numero = self.numeros[self.indice_numero]
        self.indice_numero += 1
        return numero
    
    def generar_tiempo_entre_arribos(self, turno: str) -> int:
        """
        Genera tiempo entre arribos según el turno usando método función inversa.
        
        Args:
            turno: "mañana" o "tarde"
            
        Returns:
            int: Tiempo entre arribos en minutos
        """
        ri = self.obtener_numero_aleatorio()
        
        if turno == "mañana":
            # Uniforme Discreta [1, 14] → xi = 1 + 13*ri
            return int(1 + 13 * ri)
        else:  # turno == "tarde"
            # Uniforme Discreta [4, 20] → xi = 4 + 16*ri  
            return int(4 + 16 * ri)
    
    def generar_tiempo_atencion(self) -> int:
        """
        Genera tiempo de atención usando método función inversa.
        
        Returns:
            int: Tiempo de atención en minutos
        """
        ri = self.obtener_numero_aleatorio()
        # Uniforme Discreta [3, 20] → xi = 3 + 17*ri
        return int(3 + 17 * ri)
    
    def evaluar_arrepentimiento(self, tiempo_espera_estimado: float) -> bool:
        """
        Evalúa si un cliente se arrepiente basado en tiempo de espera estimado.
        
        Args:
            tiempo_espera_estimado: Tiempo estimado de espera en minutos
            
        Returns:
            bool: True si el cliente se va, False si se queda
        """
        ri = self.obtener_numero_aleatorio()
        
        if tiempo_espera_estimado >= 25:
            # 96% se va, 4% se queda
            return ri <= 0.96
        elif tiempo_espera_estimado >= 20:
            # 45% se va, 55% se queda  
            return ri <= 0.45
        elif tiempo_espera_estimado >= 15:
            # 20% se va, 80% se queda
            return ri <= 0.20
        else:
            # No hay arrepentimiento si espera < 15 min
            return False
    
    def buscar_cola_menor(self, personas_en_sistema: List[int]) -> int:
        """
        Encuentra el servidor con menor cantidad de personas en cola.
        
        Args:
            personas_en_sistema: Lista con cantidad de personas por servidor
            
        Returns:
            int: Índice del servidor con menor cola (0-indexado)
        """
        return personas_en_sistema.index(min(personas_en_sistema))
    
    def estimar_tiempo_espera(self, servidor_idx: int, personas_en_sistema: List[int], 
                            tiempo_proxima_salida: List[float], tiempo_actual: float) -> float:
        """
        Estima el tiempo de espera para un cliente que llega.
        
        Args:
            servidor_idx: Índice del servidor asignado
            personas_en_sistema: Cantidad de personas en cada servidor
            tiempo_proxima_salida: Tiempos de próxima salida por servidor
            tiempo_actual: Tiempo actual de simulación
            
        Returns:
            float: Tiempo de espera estimado en minutos
        """
        if personas_en_sistema[servidor_idx] == 0:
            return 0  # Atención inmediata
        else:
            # Estimar basado en personas en cola y tiempo promedio de atención
            tiempo_restante_actual = max(0, tiempo_proxima_salida[servidor_idx] - tiempo_actual)
            tiempo_espera = tiempo_restante_actual + (personas_en_sistema[servidor_idx] - 1) * 11.5  # Promedio atención
            return tiempo_espera
    
    def determinar_turno(self, tiempo_simulacion: float) -> str:
        """
        Determina el turno actual basado en el tiempo de simulación.
        
        Args:
            tiempo_simulacion: Tiempo actual en minutos desde inicio del día
            
        Returns:
            str: "mañana" o "tarde"
        """
        tiempo_dia = tiempo_simulacion % 510  # 510 min = día completo (270 + 240)
        if tiempo_dia < 270:  # 270 min = 4.5 horas turno mañana
            return "mañana"
        else:
            return "tarde"
    
    def simular_una_corrida(self, cantidad_empleados: int, tiempo_fin: float = 10200) -> EstadisticasCorrida:
        """
        Ejecuta una corrida completa de simulación.
        
        Args:
            cantidad_empleados: Número de empleados (1, 2, o 3)
            tiempo_fin: Tiempo total de simulación en minutos (20 días * 510 min/día)
            
        Returns:
            EstadisticasCorrida: Resultados de la corrida
        """
        # Inicialización de variables
        tiempo_simulacion = 0.0
        tiempo_proxima_llegada = 0.0
        personas_en_sistema = [0] * cantidad_empleados
        personas_totales_sistema = 0
        tiempo_proxima_salida = [float('inf')] * cantidad_empleados
        
        # Acumuladores
        suma_tiempo_permanencia = 0.0
        suma_tiempo_atencion = [0.0] * cantidad_empleados
        personas_atendidas = 0
        clientes_se_fueron = 0
        tiempo_maximo_espera = 0.0
        clientes_por_servidor = [0] * cantidad_empleados
        
        # Generar primera llegada
        turno = self.determinar_turno(tiempo_simulacion)
        tiempo_entre_arribos = self.generar_tiempo_entre_arribos(turno)
        tiempo_proxima_llegada = tiempo_simulacion + tiempo_entre_arribos
        
        # Bucle principal
        while tiempo_simulacion < tiempo_fin:
            # Buscar menor tiempo de próxima salida
            k = tiempo_proxima_salida.index(min(tiempo_proxima_salida))
            
            # Decisión: ¿Llegada o Salida?
            if tiempo_proxima_llegada <= tiempo_proxima_salida[k]:
                # EVENTO: LLEGADA
                # Actualizar suma tiempo permanencia
                suma_tiempo_permanencia += (tiempo_proxima_llegada - tiempo_simulacion) * personas_totales_sistema
                tiempo_simulacion = tiempo_proxima_llegada
                
                # Generar próxima llegada
                turno = self.determinar_turno(tiempo_simulacion)
                tiempo_entre_arribos = self.generar_tiempo_entre_arribos(turno)
                tiempo_proxima_llegada = tiempo_simulacion + tiempo_entre_arribos
                
                # Buscar cola con menor cantidad de personas
                servidor_asignado = self.buscar_cola_menor(personas_en_sistema)
                
                # Evaluar arrepentimiento
                tiempo_espera_estimado = self.estimar_tiempo_espera(
                    servidor_asignado, personas_en_sistema, tiempo_proxima_salida, tiempo_simulacion
                )
                
                if self.evaluar_arrepentimiento(tiempo_espera_estimado):
                    # Cliente se va sin ser atendido
                    clientes_se_fueron += 1
                else:
                    # Cliente se queda
                    personas_en_sistema[servidor_asignado] += 1
                    personas_totales_sistema += 1
                    clientes_por_servidor[servidor_asignado] += 1
                    
                    # Actualizar tiempo máximo de espera
                    tiempo_maximo_espera = max(tiempo_maximo_espera, tiempo_espera_estimado)
                    
                    # ¿Servidor libre?
                    if personas_en_sistema[servidor_asignado] == 1:
                        # Atención inmediata
                        tiempo_atencion = self.generar_tiempo_atencion()
                        tiempo_proxima_salida[servidor_asignado] = tiempo_simulacion + tiempo_atencion
                        suma_tiempo_atencion[servidor_asignado] += tiempo_atencion
            
            else:
                # EVENTO: SALIDA
                # Actualizar suma tiempo permanencia
                suma_tiempo_permanencia += (tiempo_proxima_salida[k] - tiempo_simulacion) * personas_totales_sistema
                tiempo_simulacion = tiempo_proxima_salida[k]
                personas_en_sistema[k] -= 1
                personas_totales_sistema -= 1
                personas_atendidas += 1
                
                # ¿Hay cola?
                if personas_en_sistema[k] >= 1:
                    # Atender siguiente cliente
                    tiempo_atencion = self.generar_tiempo_atencion()
                    tiempo_proxima_salida[k] = tiempo_simulacion + tiempo_atencion
                    suma_tiempo_atencion[k] += tiempo_atencion
                else:
                    # Servidor queda libre
                    tiempo_proxima_salida[k] = float('inf')
        
        # Calcular estadísticas finales
        tiempo_promedio_permanencia = suma_tiempo_permanencia / personas_atendidas if personas_atendidas > 0 else 0
        tiempo_promedio_atencion = sum(suma_tiempo_atencion) / personas_atendidas if personas_atendidas > 0 else 0
        
        return EstadisticasCorrida(
            tiempo_promedio_permanencia=tiempo_promedio_permanencia,
            tiempo_maximo_espera=tiempo_maximo_espera,
            tiempo_promedio_atencion=tiempo_promedio_atencion,
            clientes_atendidos_total=personas_atendidas,
            clientes_se_fueron=clientes_se_fueron,
            servidor_1_clientes=clientes_por_servidor[0],
            servidor_2_clientes=clientes_por_servidor[1] if cantidad_empleados >= 2 else 0,
            servidor_3_clientes=clientes_por_servidor[2] if cantidad_empleados >= 3 else 0
        )
    
    def ejecutar_experimento(self, configuraciones_empleados: List[int] = [1, 2, 3], 
                           corridas_por_config: int = 50) -> Dict:
        """
        Ejecuta el experimento completo con múltiples configuraciones y corridas.
        
        Args:
            configuraciones_empleados: Lista de configuraciones a evaluar
            corridas_por_config: Número de corridas por configuración
            
        Returns:
            Dict: Resultados consolidados del experimento
        """
        resultados = {}
        
        for config in configuraciones_empleados:
            print(f"\n🔄 Ejecutando {corridas_por_config} corridas con {config} empleado(s)...")
            
            corridas = []
            for corrida in range(corridas_por_config):
                if (corrida + 1) % 10 == 0:
                    print(f"  Corrida {corrida + 1}/{corridas_por_config}")
                
                # Reiniciar índice de números para cada corrida
                self.indice_numero = (corrida * 1000) % len(self.numeros)
                
                estadisticas = self.simular_una_corrida(config)
                corridas.append(estadisticas)
            
            # Calcular estadísticas consolidadas
            resultados[config] = self.calcular_estadisticas_consolidadas(corridas, config)
        
        return resultados
    
    def calcular_estadisticas_consolidadas(self, corridas: List[EstadisticasCorrida], 
                                         num_empleados: int) -> Dict:
        """
        Calcula estadísticas consolidadas de múltiples corridas.
        
        Args:
            corridas: Lista de estadísticas de corridas individuales
            num_empleados: Número de empleados de la configuración
            
        Returns:
            Dict: Estadísticas consolidadas
        """
        if not corridas:
            return {}
        
        tiempos_permanencia = [c.tiempo_promedio_permanencia for c in corridas]
        tiempos_maximos = [c.tiempo_maximo_espera for c in corridas]
        tiempos_atencion = [c.tiempo_promedio_atencion for c in corridas]
        clientes_atendidos = [c.clientes_atendidos_total for c in corridas]
        clientes_perdidos = [c.clientes_se_fueron for c in corridas]
        
        return {
            "num_empleados": num_empleados,
            "corridas": len(corridas),
            "tiempo_permanencia_promedio": np.mean(tiempos_permanencia),
            "tiempo_permanencia_std": np.std(tiempos_permanencia),
            "tiempo_maximo_espera_promedio": np.mean(tiempos_maximos),
            "tiempo_maximo_espera_max": np.max(tiempos_maximos),
            "tiempo_atencion_promedio": np.mean(tiempos_atencion),
            "clientes_atendidos_promedio": np.mean(clientes_atendidos),
            "clientes_perdidos_promedio": np.mean(clientes_perdidos),
            "porcentaje_perdida_clientes": np.mean(clientes_perdidos) / (np.mean(clientes_atendidos) + np.mean(clientes_perdidos)) * 100,
            "cumple_objetivo_6min": np.mean(tiempos_maximos) <= 6.0,
            "corridas_que_cumplen": sum(1 for t in tiempos_maximos if t <= 6.0),
            "porcentaje_corridas_exitosas": sum(1 for t in tiempos_maximos if t <= 6.0) / len(tiempos_maximos) * 100
        }

def cargar_numeros_pseudoaleatorios(archivo: str = "numeros_pseudoaleatorios.csv") -> List[float]:
    """
    Carga números pseudoaleatorios desde archivo CSV.
    
    Args:
        archivo: Nombre del archivo CSV
        
    Returns:
        List[float]: Lista de números pseudoaleatorios
    """
    numeros = []
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                numeros.append(float(row['numero_pseudoaleatorio']))
        print(f"✅ Cargados {len(numeros)} números pseudoaleatorios desde {archivo}")
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {archivo}")
        print("Ejecuta primero 'numeros_pseudoaleatorios.py' para generar los números")
        raise
    
    return numeros

def exportar_resultados(resultados: Dict, archivo: str = "resultados_simulacion.csv"):
    """
    Exporta resultados consolidados a CSV.
    
    Args:
        resultados: Diccionario con resultados por configuración
        archivo: Nombre del archivo de salida
    """
    datos = []
    for config, stats in resultados.items():
        datos.append({
            "num_empleados": config,
            "tiempo_permanencia_promedio": round(stats["tiempo_permanencia_promedio"], 2),
            "tiempo_maximo_espera_promedio": round(stats["tiempo_maximo_espera_promedio"], 2),
            "tiempo_maximo_espera_max": round(stats["tiempo_maximo_espera_max"], 2),
            "clientes_atendidos_promedio": round(stats["clientes_atendidos_promedio"], 1),
            "clientes_perdidos_promedio": round(stats["clientes_perdidos_promedio"], 1),
            "porcentaje_perdida_clientes": round(stats["porcentaje_perdida_clientes"], 2),
            "cumple_objetivo_6min": stats["cumple_objetivo_6min"],
            "porcentaje_corridas_exitosas": round(stats["porcentaje_corridas_exitosas"], 1)
        })
    
    df = pd.DataFrame(datos)
    df.to_csv(archivo, index=False, encoding='utf-8')
    print(f"✅ Resultados exportados a: {archivo}")

def main():
    """Función principal del programa de simulación."""
    print("🏪 Simulación Ferretería JYL - Sistema de Colas")
    print("=" * 60)
    
    try:
        # Cargar números pseudoaleatorios validados
        numeros = cargar_numeros_pseudoaleatorios()
        
        # Inicializar simulador
        simulador = SimuladorFerreteria(numeros)
        
        # Ejecutar experimento
        print("\n🧪 Iniciando experimento de simulación...")
        resultados = simulador.ejecutar_experimento()
        
        # Mostrar resultados
        print("\n📊 RESULTADOS CONSOLIDADOS:")
        print("=" * 60)
        
        for config, stats in resultados.items():
            print(f"\n👥 {config} EMPLEADO(S):")
            print(f"  Tiempo permanencia promedio: {stats['tiempo_permanencia_promedio']:.2f} min")
            print(f"  Tiempo máximo espera promedio: {stats['tiempo_maximo_espera_promedio']:.2f} min")
            print(f"  Tiempo máximo espera (peak): {stats['tiempo_maximo_espera_max']:.2f} min")
            print(f"  Clientes atendidos promedio: {stats['clientes_atendidos_promedio']:.1f}")
            print(f"  Clientes perdidos promedio: {stats['clientes_perdidos_promedio']:.1f}")
            print(f"  % pérdida de clientes: {stats['porcentaje_perdida_clientes']:.2f}%")
            print(f"  Cumple objetivo (≤6 min): {'✅ SÍ' if stats['cumple_objetivo_6min'] else '❌ NO'}")
            print(f"  % corridas exitosas: {stats['porcentaje_corridas_exitosas']:.1f}%")
        
        # Exportar resultados
        exportar_resultados(resultados)
        
        # Recomendación
        print("\n🎯 RECOMENDACIÓN:")
        empleados_optimos = None
        for config, stats in resultados.items():
            if stats['cumple_objetivo_6min']:
                empleados_optimos = config
                break
        
        if empleados_optimos:
            print(f"Se recomienda contratar {empleados_optimos} empleado(s) para cumplir el objetivo.")
        else:
            print("Ninguna configuración cumple el objetivo de ≤6 min. Se requiere análisis adicional.")
        
    except Exception as e:
        print(f"❌ Error en la simulación: {e}")

if __name__ == "__main__":
    main() 