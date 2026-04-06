SELECT
    c.ClienteId,
    c.Nombre,
    p.PedidoId,
    p.Monto
FROM dbo.Clientes c
INNER JOIN dbo.Pedidos p
    ON c.ClienteId = p.ClienteId;