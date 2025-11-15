
CREATE TYPE ROL_EMPLEADO AS ENUM ('empleado', 'admin');
CREATE TYPE METODO_PAGO AS ENUM ('efectivo', 'tarjeta de credito', 'transferencia bancaria');

-- 1. Tabla de Empleados (Para control de acceso y registro de movimientos)
CREATE TABLE Empleados (
    id_empleado SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    usuario VARCHAR(100) NOT NULL UNIQUE,
    hash_contrasena TEXT NOT NULL,
    rol ROL_EMPLEADO NOT NULL DEFAULT 'empleado',
    activo BOOLEAN DEFAULT TRUE
);

-- 2. Tabla de Clientes
CREATE TABLE Clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    direccion TEXT,
    correo_electronico VARCHAR(255) UNIQUE,
    telefono VARCHAR(50)
);

-- 3. Tabla de Proveedores
CREATE TABLE Proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre_proveedor VARCHAR(255) NOT NULL,
    datos_contacto TEXT -- Flexible para guardar email, teléfono, dirección, etc.
);

-- 4. Tabla de Categorias de Productos
CREATE TABLE Categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- 5. Tabla de Productos (definir el producto "padre" o "plantilla")
CREATE TABLE Productos (
    id_producto SERIAL PRIMARY KEY,
    id_categoria INT NOT NULL,
    descripcion TEXT NOT NULL,
    precio_base DECIMAL(10, 2) NOT NULL CHECK (precio_base >= 0),
    
    CONSTRAINT fk_categoria
        FOREIGN KEY(id_categoria) 
        REFERENCES Categorias(id_categoria)
        ON DELETE RESTRICT -- No dejar borrar una categoría si tiene productos
);

-- 6. Tabla de Variantes (inventario real)
-- Un producto (ej. "Camiseta Logo") tiene multiples variantes (Talla M/Rojo, Talla M/Azul, etc.)
CREATE TABLE Variantes_Producto (
    id_variante SERIAL PRIMARY KEY,
    id_producto INT NOT NULL,
    talla VARCHAR(50),
    color VARCHAR(50),
    stock_disponible INT NOT NULL DEFAULT 0 CHECK (stock_disponible >= 0),
    
    CONSTRAINT fk_producto
        FOREIGN KEY(id_producto) 
        REFERENCES Productos(id_producto)
        ON DELETE CASCADE, -- Si se borra el producto, se borran sus variantes
        
    UNIQUE(id_producto, talla, color) -- Un producto no puede tener dos variantes "Talla M / Color Rojo"
);

-- 7. Tabla N-M para vincular Productos y Proveedores
CREATE TABLE Proveedores_Productos (
    id_proveedor INT NOT NULL,
    id_producto INT NOT NULL,
    
    PRIMARY KEY (id_proveedor, id_producto),
    CONSTRAINT fk_proveedor
        FOREIGN KEY(id_proveedor) 
        REFERENCES Proveedores(id_proveedor),
    CONSTRAINT fk_producto
        FOREIGN KEY(id_producto) 
        REFERENCES Productos(id_producto)
);

-- 8. Tabla de Descuentos y Promociones
CREATE TABLE Descuentos (
    id_descuento SERIAL PRIMARY KEY,
    id_producto INT NOT NULL, -- Descuento aplicado a un producto específico
    porcentaje DECIMAL(5, 2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    
    CONSTRAINT fk_producto
        FOREIGN KEY(id_producto) 
        REFERENCES Productos(id_producto)
        ON DELETE CASCADE,
        
    CHECK (fecha_fin >= fecha_inicio) -- La fecha de fin debe ser posterior o igual a la de inicio
);

-- 9. Tabla de Ventas (el "ticket" o "encabezado" de la transaccion)
CREATE TABLE Ventas (
    id_venta SERIAL PRIMARY KEY,
    id_cliente INT, -- Puede ser NULO si es un cliente no registrado
    id_empleado INT NOT NULL,
    fecha_venta TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_pago METODO_PAGO NOT NULL,
    monto_total_venta DECIMAL(10, 2) NOT NULL,
    
    CONSTRAINT fk_cliente
        FOREIGN KEY(id_cliente) 
        REFERENCES Clientes(id_cliente)
        ON DELETE SET NULL, -- Si se borra un cliente, la venta no se borra
        
    CONSTRAINT fk_empleado
        FOREIGN KEY(id_empleado) 
        REFERENCES Empleados(id_empleado)
);

-- 10. Tabla de Detalles de Venta (los productos dentro del ticket)
CREATE TABLE Detalles_Venta (
    id_detalle_venta SERIAL PRIMARY KEY,
    id_venta INT NOT NULL,
    id_variante INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario_venta DECIMAL(10, 2) NOT NULL, -- Precio al momento de la venta (por si el precio base cambia)
    descuento_aplicado DECIMAL(10, 2) DEFAULT 0, -- Para descuentos manuales en el punto de venta
    
    CONSTRAINT fk_venta
        FOREIGN KEY(id_venta) 
        REFERENCES Ventas(id_venta)
        ON DELETE CASCADE, -- Si se borra la venta, se borran sus detalles
        
    CONSTRAINT fk_variante
        FOREIGN KEY(id_variante) 
        REFERENCES Variantes_Producto(id_variante)
        ON DELETE RESTRICT -- No permitir borrar una variante si ya fue vendida (importante para historial)
);

-- 11. Tabla de Log de Movimientos (requerimiento de auditoria de empleados)
CREATE TABLE Log_Movimientos (
    id_log SERIAL PRIMARY KEY,
    id_empleado INT NOT NULL,
    fecha_movimiento TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(255) NOT NULL, -- Ej: "actualizacion de precio", "ajuste de inventario"
    descripcion_detallada TEXT,
    
    CONSTRAINT fk_empleado
        FOREIGN KEY(id_empleado) 
        REFERENCES Empleados(id_empleado)
);