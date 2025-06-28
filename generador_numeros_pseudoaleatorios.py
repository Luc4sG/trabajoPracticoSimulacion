"""
Generador de Números Pseudoaleatorios con Validación
Ferretería JYL - Trabajo Práctico de Simulación

Este módulo genera números pseudoaleatorios que pasan todas las pruebas de aleatoriedad:
- Prueba de la media
- Prueba de la varianza  
- Prueba de chi-cuadrado
- Prueba de corridas arriba-abajo

Autor: [Tu nombre]
Fecha: 2025
"""

import numpy as np
import pandas as pd
import math
from scipy import stats
from typing import List, Tuple, Dict
import csv

class GeneradorPseudoaleatorios:
    def __init__(self, semilla: int = 12345):
        """
        Inicializa el generador con una semilla.
        
        Args:
            semilla: Semilla inicial para el generador
        """
        self.semilla_inicial = semilla
        self.reset()
    
    def reset(self):
        """Reinicia el generador con la semilla inicial."""
        self.semilla = self.semilla_inicial
    
    def generar_numero(self) -> float:
        """
        Genera un número pseudoaleatorio usando método congruencial lineal mixto.
        
        Parámetros del generador:
        - a = 1664525 (multiplicador)
        - c = 1013904223 (incremento)  
        - m = 2^32 (módulo)
        
        Returns:
            float: Número pseudoaleatorio en [0,1)
        """
        a = 1664525
        c = 1013904223
        m = 2**32
        
        self.semilla = (a * self.semilla + c) % m
        return self.semilla / m
    
    def generar_secuencia(self, n: int) -> List[float]:
        """
        Genera una secuencia de n números pseudoaleatorios.
        
        Args:
            n: Cantidad de números a generar
            
        Returns:
            List[float]: Lista de números pseudoaleatorios
        """
        return [self.generar_numero() for _ in range(n)]

class ValidadorAleatoriedad:
    """Clase para validar la aleatoriedad de secuencias de números."""
    
    @staticmethod
    def prueba_media(numeros: List[float], n: int = 100, alpha: float = 0.05) -> Dict:
        """
        Prueba de la media: compara la media muestral con 0.5.
        
        Args:
            numeros: Secuencia de números a validar
            n: Tamaño de muestra para la prueba
            alpha: Nivel de significancia
            
        Returns:
            Dict: Resultados de la prueba
        """
        if len(numeros) < n:
            return {"aprobada": False, "razon": f"Insuficientes datos (mín: {n})"}
        
        muestra = numeros[:n]
        media_muestral = np.mean(muestra)
        media_teorica = 0.5
        varianza_teorica = 1/12
        
        # Intervalo de confianza para la media
        z_alpha_2 = stats.norm.ppf(1 - alpha/2)
        error_estandar = math.sqrt(varianza_teorica / n)
        limite_inferior = media_teorica - z_alpha_2 * error_estandar
        limite_superior = media_teorica + z_alpha_2 * error_estandar
        
        aprobada = limite_inferior <= media_muestral <= limite_superior
        
        return {
            "aprobada": aprobada,
            "media_muestral": media_muestral,
            "media_teorica": media_teorica,
            "limite_inferior": limite_inferior,
            "limite_superior": limite_superior,
            "dentro_intervalo": aprobada
        }
    
    @staticmethod
    def prueba_varianza(numeros: List[float], n: int = 100, alpha: float = 0.05) -> Dict:
        """
        Prueba de la varianza: contrasta varianza muestral con 1/12.
        
        Args:
            numeros: Secuencia de números a validar
            n: Tamaño de muestra
            alpha: Nivel de significancia
            
        Returns:
            Dict: Resultados de la prueba
        """
        if len(numeros) < n:
            return {"aprobada": False, "razon": f"Insuficientes datos (mín: {n})"}
        
        muestra = numeros[:n]
        varianza_muestral = np.var(muestra, ddof=1)  # ddof=1 para muestra
        varianza_teorica = 1/12
        
        # Estadístico chi-cuadrado para varianza
        chi2_obs = (n - 1) * varianza_muestral / varianza_teorica
        
        # Valores críticos
        chi2_inferior = stats.chi2.ppf(alpha/2, n-1)
        chi2_superior = stats.chi2.ppf(1-alpha/2, n-1)
        
        aprobada = chi2_inferior <= chi2_obs <= chi2_superior
        
        return {
            "aprobada": aprobada,
            "varianza_muestral": varianza_muestral,
            "varianza_teorica": varianza_teorica,
            "chi2_observado": chi2_obs,
            "chi2_inferior": chi2_inferior,
            "chi2_superior": chi2_superior,
            "dentro_intervalo": aprobada
        }
    
    @staticmethod
    def prueba_chi_cuadrado(numeros: List[float], k: int = 10, alpha: float = 0.05) -> Dict:
        """
        Prueba de chi-cuadrado: divide [0,1) en k intervalos y verifica uniformidad.
        
        Args:
            numeros: Secuencia de números a validar
            k: Número de intervalos
            alpha: Nivel de significancia
            
        Returns:
            Dict: Resultados de la prueba
        """
        n = len(numeros)
        if n < k * 5:  # Regla empírica: al menos 5 observaciones por intervalo
            return {"aprobada": False, "razon": f"Insuficientes datos (mín: {k*5})"}
        
        # Crear intervalos
        intervalos = np.linspace(0, 1, k+1)
        
        # Contar observaciones por intervalo
        observadas = np.histogram(numeros, bins=intervalos)[0]
        
        # Frecuencias esperadas (uniformemente distribuidas)
        esperadas = np.full(k, n/k)
        
        # Estadístico chi-cuadrado
        chi2_obs = np.sum((observadas - esperadas)**2 / esperadas)
        
        # Valor crítico
        grados_libertad = k - 1
        chi2_critico = stats.chi2.ppf(1-alpha, grados_libertad)
        
        aprobada = chi2_obs <= chi2_critico
        
        return {
            "aprobada": aprobada,
            "chi2_observado": chi2_obs,
            "chi2_critico": chi2_critico,
            "grados_libertad": grados_libertad,
            "observadas": observadas.tolist(),
            "esperadas": esperadas.tolist(),
            "intervalos": k
        }
    
    @staticmethod
    def prueba_corridas(numeros: List[float], alpha: float = 0.05) -> Dict:
        """
        Prueba de corridas arriba-abajo: analiza independencia de la secuencia.
        
        Args:
            numeros: Secuencia de números a validar
            alpha: Nivel de significancia
            
        Returns:
            Dict: Resultados de la prueba
        """
        n = len(numeros)
        if n < 20:
            return {"aprobada": False, "razon": "Insuficientes datos (mín: 20)"}
        
        mediana = np.median(numeros)
        
        # Convertir a secuencia de símbolos (arriba/abajo de la mediana)
        simbolos = ['+' if x >= mediana else '-' for x in numeros]
        
        # Contar corridas
        corridas = 1
        for i in range(1, len(simbolos)):
            if simbolos[i] != simbolos[i-1]:
                corridas += 1
        
        # Contar elementos arriba y abajo de la mediana
        n1 = simbolos.count('+')  # arriba
        n2 = simbolos.count('-')  # abajo
        
        # Media y varianza teóricas del número de corridas
        if n1 == 0 or n2 == 0:
            return {"aprobada": False, "razon": "Todos los valores en un lado de la mediana"}
        
        mu_r = (2 * n1 * n2) / (n1 + n2) + 1
        var_r = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
        
        # Aproximación normal para el test
        if var_r <= 0:
            return {"aprobada": False, "razon": "Varianza inválida"}
        
        z = (corridas - mu_r) / math.sqrt(var_r)
        
        # Valor crítico (test de dos colas)
        z_critico = stats.norm.ppf(1 - alpha/2)
        
        aprobada = abs(z) <= z_critico
        
        return {
            "aprobada": aprobada,
            "corridas_observadas": corridas,
            "corridas_esperadas": mu_r,
            "varianza_corridas": var_r,
            "z_estadistico": z,
            "z_critico": z_critico,
            "n_arriba": n1,
            "n_abajo": n2,
            "mediana": mediana
        }

def generar_numeros_validados(n_numeros: int = 1000, max_intentos: int = 100) -> Tuple[List[float], Dict]:
    """
    Genera números pseudoaleatorios que pasan todas las pruebas de aleatoriedad.
    
    Args:
        n_numeros: Cantidad de números a generar
        max_intentos: Máximo número de intentos
        
    Returns:
        Tuple[List[float], Dict]: Números validados y resultados de pruebas
    """
    generador = GeneradorPseudoaleatorios()
    validador = ValidadorAleatoriedad()
    
    for intento in range(max_intentos):
        print(f"Intento {intento + 1}/{max_intentos}...")
        
        # Generar nueva secuencia
        generador.reset()
        generador.semilla = generador.semilla_inicial + intento * 1000  # Cambiar semilla
        numeros = generador.generar_secuencia(n_numeros)
        
        # Ejecutar todas las pruebas
        resultado_media = validador.prueba_media(numeros)
        resultado_varianza = validador.prueba_varianza(numeros)
        resultado_chi2 = validador.prueba_chi_cuadrado(numeros)
        resultado_corridas = validador.prueba_corridas(numeros)
        
        # Verificar si todas las pruebas pasan
        todas_aprobadas = (
            resultado_media["aprobada"] and
            resultado_varianza["aprobada"] and
            resultado_chi2["aprobada"] and
            resultado_corridas["aprobada"]
        )
        
        resultados = {
            "intento": intento + 1,
            "semilla_utilizada": generador.semilla_inicial + intento * 1000,
            "media": resultado_media,
            "varianza": resultado_varianza,
            "chi_cuadrado": resultado_chi2,
            "corridas": resultado_corridas,
            "todas_aprobadas": todas_aprobadas
        }
        
        if todas_aprobadas:
            print("✅ ¡Todas las pruebas aprobadas!")
            return numeros, resultados
        else:
            pruebas_fallidas = []
            if not resultado_media["aprobada"]:
                pruebas_fallidas.append("media")
            if not resultado_varianza["aprobada"]:
                pruebas_fallidas.append("varianza")
            if not resultado_chi2["aprobada"]:
                pruebas_fallidas.append("chi-cuadrado")
            if not resultado_corridas["aprobada"]:
                pruebas_fallidas.append("corridas")
            
            print(f"❌ Fallaron: {', '.join(pruebas_fallidas)}")
    
    raise Exception(f"No se pudieron generar números válidos en {max_intentos} intentos")

def exportar_csv(numeros: List[float], archivo: str = "numeros_pseudoaleatorios_validados.csv"):
    """
    Exporta los números validados a un archivo CSV.
    
    Args:
        numeros: Lista de números a exportar
        archivo: Nombre del archivo de salida
    """
    with open(archivo, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["indice", "numero_pseudoaleatorio"])
        for i, numero in enumerate(numeros):
            writer.writerow([i+1, numero])
    
    print(f"✅ Números exportados a: {archivo}")

def main():
    """Función principal del programa."""
    print("🎲 Generador de Números Pseudoaleatorios - Ferretería JYL")
    print("=" * 60)
    
    try:
        # Generar números validados
        numeros, resultados = generar_numeros_validados(n_numeros=1000)
        
        # Mostrar resumen de resultados
        print("\n📊 RESUMEN DE VALIDACIÓN:")
        print(f"Semilla utilizada: {resultados['semilla_utilizada']}")
        print(f"Números generados: {len(numeros)}")
        print("\nResultados de pruebas:")
        print(f"  • Media: {'✅ APROBADA' if resultados['media']['aprobada'] else '❌ RECHAZADA'}")
        print(f"  • Varianza: {'✅ APROBADA' if resultados['varianza']['aprobada'] else '❌ RECHAZADA'}")
        print(f"  • Chi-cuadrado: {'✅ APROBADA' if resultados['chi_cuadrado']['aprobada'] else '❌ RECHAZADA'}")
        print(f"  • Corridas: {'✅ APROBADA' if resultados['corridas']['aprobada'] else '❌ RECHAZADA'}")
        
        # Exportar a CSV
        exportar_csv(numeros)
        
        print("\n🎯 Los números generados superaron todas las pruebas de aleatoriedad.")
        print("Están listos para usar en la simulación de la ferretería.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 