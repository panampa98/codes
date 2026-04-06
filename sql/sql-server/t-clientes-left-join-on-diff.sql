SELECT
    c.ClienteId,
    c.Nombre,
    p.PedidoId,
    p.Monto
FROM dbo.Clientes c
INNER JOIN dbo.Pedidos p
    ON c.ClienteId = p.ClienteId
        AND p.Monto > 100;

SELECT
    c.ClienteId,
    c.Nombre,
    p.PedidoId,
    p.Monto
FROM dbo.Clientes c
LEFT JOIN dbo.Pedidos p
    ON c.ClienteId = p.ClienteId
WHERE p.Monto > 100;


SELECT
    c.ClienteId,
    c.Nombre,
    p.PedidoId,
    p.Monto,
    CASE WHEN p.Monto > 100 THEN 1 ELSE 0 END flg_amt_gt100
FROM dbo.Clientes c
LEFT JOIN dbo.Pedidos p
    ON c.ClienteId = p.ClienteId;