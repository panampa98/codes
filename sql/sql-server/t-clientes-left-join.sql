SELECT
    c.ClienteId,
    c.Nombre,
    p.PedidoId,
    p.Monto
FROM dbo.Clientes c
LEFT JOIN dbo.Pedidos p
    ON c.ClienteId = p.ClienteId
--WHERE p.ClienteId IS NOT NULL;
WHERE p.Monto > 100