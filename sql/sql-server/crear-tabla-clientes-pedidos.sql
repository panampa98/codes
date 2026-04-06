-- Limpieza previa
IF OBJECT_ID('dbo.Pedidos', 'U') IS NOT NULL
    DROP TABLE dbo.Pedidos;

IF OBJECT_ID('dbo.Clientes', 'U') IS NOT NULL
    DROP TABLE dbo.Clientes;


-- Tabla principal
CREATE TABLE dbo.Clientes (
    ClienteId INT PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL
);

-- Tabla relacionada
CREATE TABLE dbo.Pedidos (
    PedidoId INT PRIMARY KEY,
    ClienteId INT NOT NULL,
    Monto DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ClienteId) REFERENCES dbo.Clientes(ClienteId)
);


-- Datos de ejemplo
INSERT INTO dbo.Clientes (ClienteId, Nombre)
VALUES
    (1, 'Ana'),
    (2, 'Luis'),
    (3, 'Carla'),
    (4, 'Diego');

INSERT INTO dbo.Pedidos (PedidoId, ClienteId, Monto)
VALUES
    (101, 1, 120.00),
    (102, 1, 80.00),
    (103, 3, 200.00);


SELECT * FROM dbo.Clientes;
SELECT * FROM dbo.Pedidos;