from mis_trapitos.database_conexion.reporte_queries import ReportQueries
from mis_trapitos.core.logger import log

class ReportGenerator:
    """
    Controlador lógico para la generación de reportes.
    Se encarga de invocar las consultas de lectura y manejar posibles errores
    antes de entregar los datos a la vista.
    """

    def __init__(self):
        """Inicializa la instancia de consultas de reportes"""
        self.queries = ReportQueries()

    def obtenerResumenInventario(self):
        """
        Genera el reporte del producto con mayor stock.
        Retorna: Diccionario con datos o mensaje de vacío.
        """
        try:
            datos = self.queries.obtenerProductoMayorStock()
            if datos:
                # datos = (descripcion, talla, color, stock)
                return {
                    "producto": datos[0],
                    "variante": f"{datos[1]} / {datos[2]}",
                    "stock": datos[3]
                }
            return None
        except Exception as e:
            log.error(f"Error al generar reporte de inventario: {e}")
            return None

    def obtenerProductosEstancados(self, dias=90):
        """
        Obtiene lista de productos sin ventas en el periodo indicado.
        """
        try:
            # datos es una lista de tuplas: [(desc, talla, color), ...]
            lista_cruda = self.queries.obtenerProductosSinVentas(dias)
            return lista_cruda
        except Exception as e:
            log.error(f"Error al obtener productos estancados: {e}")
            return []

    def obtenerTendenciasPago(self):
        """
        Retorna estadísticas de uso de métodos de pago.
        """
        try:
            return self.queries.obtenerMetodosPagoPopulares()
        except Exception as e:
            log.error(f"Error en reporte de pagos: {e}")
            return []

    def obtenerTopVentasMes(self):
        """
        Retorna los 5 productos más vendidos de los últimos 30 días.
        """
        try:
            return self.queries.obtenerProductosMasVendidosMes()
        except Exception as e:
            log.error(f"Error en reporte top ventas: {e}")
            return []

    def obtenerMetricasRapidas(self):
        """
        Genera un resumen ejecutivo para el dashboard principal (KPIs).
        Retorna un diccionario con valores clave.
        """
        try:
            ventas_3dias = self.queries.contarVentasRecientes(3)
            mejor_oferta = self.queries.obtenerProductoMayorDescuento() # (desc, porcentaje)
            
            resumen = {
                "ventas_recientes": ventas_3dias,
                "mejor_descuento": f"{mejor_oferta[1]}% en {mejor_oferta[0]}" if mejor_oferta else "N/A"
            }
            return resumen
        except Exception as e:
            log.error(f"Error obteniendo métricas rápidas: {e}")
            return {"ventas_recientes": 0, "mejor_descuento": "N/A"}

    def buscarFidelidadCliente(self, id_cliente):
        """
        Busca productos que un cliente compra recurrentemente.
        """
        try:
            if not id_cliente:
                return []
            return self.queries.obtenerProductosRecurrentesCliente(id_cliente)
        except Exception as e:
            log.error(f"Error reporte fidelidad cliente {id_cliente}: {e}")
            return []

    def buscarProductosPremium(self, precio_minimo):
        """
        Lista productos por encima de cierto precio que tienen stock.
        """
        try:
            precio = float(precio_minimo)
            return self.queries.buscarProductosCarosEnStock(precio)
        except ValueError:
            return []
        except Exception as e:
            log.error(f"Error reporte productos premium: {e}")
            return []
