# Documentación del Diagrama de Simulación - Ferretería
## Simulación de Eventos Discretos para Sistema de Colas

---

## 📋 **Introducción**

Este documento explica paso a paso el funcionamiento del diagrama de simulación evento a evento para una ferretería con múltiples servidores y colas. El objetivo es determinar cuántos empleados se necesitan para mantener los tiempos de espera bajo 10 minutos.

---

## 🚀 **1. INICIALIZACIÓN DEL SISTEMA**

### Variables Iniciales:
```
tiempo_simulacion = 0                 // Reloj de la simulación
tiempo_proxima_llegada = 0           // Próximo cliente que llega
personas_en_sistema = 0              // Personas totales en el sistema
cantidad_servidores = n              // Número de empleados/servidores
suma_tiempo_permanencia = 0          // Acumulador tiempo en sistema
suma_tiempo_atencion = 0             // Acumulador tiempo de servicio
personas_atendidas = 0               // Contador de clientes atendidos
vi = 1..n                           // Índices para cada servidor
```

### Estado Inicial:
- Sistema vacío (sin clientes)
- Todos los servidores libres
- Contadores en cero
- Listo para comenzar la simulación

---

## 🔄 **2. BUCLE PRINCIPAL DE SIMULACIÓN**

**Condición del bucle:** `tiempo_simulacion < tiempo_fin`

El bucle continúa hasta alcanzar el tiempo límite de simulación establecido.

### 2.1 **Identificación del Próximo Evento**

```
Buscar el menor tiempo_proxima_salida_i
k = argmin(TPS[1..n])
```

**Propósito:** Determinar cuál servidor terminará primero su servicio actual.

---

## 🌟 **3. DECISIÓN PRINCIPAL: ¿LLEGADA O SALIDA?**

### Condición: `tiempo_proxima_llegada <= tiempo_proxima_salida_k`

---

## 🔵 **CAMINO A: EVENTO DE LLEGADA** (SI)

### 3.1 **Actualización del Tiempo del Sistema**
```
suma_tiempo_permanencia += (tiempo_proxima_llegada - tiempo_simulacion) * personas_totales_sistema
tiempo_simulacion = tiempo_proxima_llegada
```

**Explicación:** 
- Calcula el tiempo que todas las personas actuales permanecieron en el sistema
- Avanza el reloj de simulación al momento de la llegada

### 3.2 **Generación del Próximo Cliente**
```
Generar tiempo_entre_arribos
tiempo_proxima_llegada = tiempo_simulacion + tiempo_entre_arribos
```

**Explicación:** Programa cuándo llegará el siguiente cliente (distribución uniforme discreta por turnos).

### 3.3 **Asignación de Cola**
```
Buscar en Cola del Menor cantidad de Personas
```

**Algoritmo:** El cliente elige la cola con menor número de personas esperando.

### 3.4 **Proceso de Arrepentimiento**
```
Tratar Arrepentimiento
```

**Rangos de decisión:**
- **15+ min de espera:** 20% se va (80% se queda)
- **20+ min de espera:** 45% se va (50% se queda)  
- **25+ min de espera:** 96% se va (10% se queda)

**Caminos posibles:**
- **Cliente se va:** Sale del sistema sin ser atendido
- **Cliente se queda:** Continúa al siguiente paso

### 3.5 **Incorporación al Sistema** (Solo si no se arrepiente)
```
personas_en_sistema_k += 1
personas_totales_sistema += 1
```

### 3.6 **Decisión de Atención Inmediata**

**Condición:** `personas_en_sistema_k = 1`

#### 🟢 **CAMINO A1: SERVIDOR LIBRE** (SI)
```
Generar tiempo_atencion
tiempo_proxima_salida_k = tiempo_simulacion + tiempo_atencion
suma_tiempo_atencion_k += tiempo_atencion
```

**Explicación:** 
- El cliente es atendido inmediatamente
- Se genera un tiempo de servicio aleatorio
- Se programa cuándo terminará el servicio

#### 🟡 **CAMINO A2: SERVIDOR OCUPADO** (NO)
```
// Cliente va a cola, no se asigna tiempo de servicio aún
```

**Explicación:** 
- El cliente espera en la cola
- No se genera tiempo de servicio hasta que sea su turno

---

## 🔴 **CAMINO B: EVENTO DE SALIDA** (NO)

### 3.1 **Actualización del Tiempo del Sistema**
```
suma_tiempo_permanencia += (tiempo_proxima_salida_k - tiempo_simulacion) * personas_totales_sistema
tiempo_simulacion = tiempo_proxima_salida_k
```

**Explicación:** 
- Calcula el tiempo de permanencia de todos los clientes actuales
- Avanza el reloj al momento de la salida

### 3.2 **Liberación del Cliente**
```
personas_en_sistema_k -= 1
```

**Explicación:** Un cliente termina su servicio y sale del sistema.

### 3.3 **Decisión de Próximo Servicio**

**Condición:** `personas_en_sistema_k >= 1`

#### 🟢 **CAMINO B1: HAY COLA** (SI)
```
Generar tiempo_atencion
tiempo_proxima_salida_k = tiempo_simulacion + tiempo_atencion
suma_tiempo_atencion_k += tiempo_atencion
```

**Explicación:**
- Hay clientes esperando en cola
- El siguiente cliente comienza a ser atendido inmediatamente
- Se genera un nuevo tiempo de servicio

#### 🟡 **CAMINO B2: NO HAY COLA** (NO)
```
tiempo_proxima_salida_k = INFINITO
```

**Explicación:**
- No hay más clientes en esta cola
- El servidor queda libre
- Se marca como "sin próxima salida programada"

---

## 🏁 **4. FINALIZACIÓN DE LA SIMULACIÓN**

### Condición de Salida: `tiempo_simulacion >= tiempo_fin`

### 4.1 **Cálculo de Estadísticas Finales**
```
promedio_tiempo_permanencia = suma_tiempo_permanencia / personas_atendidas
promedio_tiempo_atencion = suma_tiempo_atencion / personas_atendidas  
porcentaje_ocupacion = suma_tiempo_atencion / tiempo_simulacion
```

### 4.2 **Métricas Clave para la Ferretería**
- **Tiempo promedio de espera:** Para evaluar si < 10 minutos
- **Porcentaje de ocupación:** Eficiencia de los empleados
- **Tiempo promedio de atención:** Duración típica del servicio

---

## 🗺️ **5. RESUMEN DE TODOS LOS CAMINOS POSIBLES**

### **Mapa de Decisiones:**

```
INICIALIZACIÓN
    ↓
┌─── BUCLE PRINCIPAL ────┐
│   ↓                    │
│   Buscar menor TPS     │
│   ↓                    │
│   ¿Llegada ≤ Salida?   │
│   ↓                    │
│ ┌─SI─┐        ┌─NO─┐   │
│ │    │        │    │   │
│ │ LLEGADA     │ SALIDA │ │
│ │    │        │    │   │
│ │ ┌─ Arrepentimiento   │ │
│ │ │  ├─Se va           │ │
│ │ │  └─Se queda        │ │
│ │ │     ↓              │ │
│ │ │  ¿Servidor libre?  │ │
│ │ │  ├─SI: Atención    │ │
│ │ │  └─NO: A cola      │ │
│ │                     │ │
│ │              ¿Hay cola? │
│ │              ├─SI: Siguiente │
│ │              └─NO: Servidor libre │
│ └─────────────────────┘ │
│   ↓                    │
│   ¿Tiempo < Fin?       │
│   ├─SI: Continuar ─────┘
│   └─NO: Finalizar
│       ↓
    ESTADÍSTICAS FINALES
```

---

## 📊 **6. ANÁLISIS DE RENDIMIENTO**

### **Indicadores Clave:**
- **Tiempo de espera < 10 min:** Objetivo principal
- **Tasa de arrepentimiento:** Pérdida de clientes
- **Utilización de servidores:** Eficiencia operativa
- **Tiempo total en sistema:** Experiencia del cliente

### **Optimización:**
El diagrama permite evaluar diferentes valores de `n` (cantidad de servidores) para encontrar el número óptimo de empleados que minimice los tiempos de espera manteniendo la eficiencia operativa.

---

## 🎯 **7. APLICACIÓN PRÁCTICA**

### **Para la Ferretería:**
1. **Ejecutar simulación** con diferentes números de empleados (n = 1, 2, 3...)
2. **Medir tiempo promedio de espera** en cada escenario
3. **Identificar el n mínimo** donde tiempo de espera < 10 minutos
4. **Considerar costos** vs beneficios de empleados adicionales
5. **Validar con datos reales** del comportamiento de clientes

---

*Este diagrama proporciona una base sólida para la toma de decisiones operativas en la ferretería, permitiendo optimizar el servicio al cliente mientras se mantiene la eficiencia del negocio.* 