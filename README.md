madmin
======

Convert from Thadmin
--------------------
* Products
```
INSERT INTO tblproduct (prd_verwijderd, prd_naam, prd_type, prd_btw,
prd_kantineprijs_leden, prd_kantineprijs_extern, prd_borrelmarge,
prd_leverancier_id, prd_emballageprijs) SELECT 0 AS prd_verwijderd, name AS
prd_naam, canteen AS prd_type, vatRate * 100 AS prd_btw,
priceDiscount AS prd_kantineprijs_leden, price AS prd_kantineprijs_extern,
margin * 100 AS prd_borrelmarge, articleNumber AS prd_leverancier_id, 0 AS
prd_emballageprijs FROM `Product` WHERE name <> '' ORDER BY prd_naam
```
```
UPDATE `tblproduct` SET prd_type = 2 WHERE prd_type = 0
UPDATE `tblproduct` SET prd_type = 3 WHERE SUBSTRING( prd_naam, 1, 9 ) = 'Emballage'
```

* Barcodes
```
SELECT identificationCode AS bar_ean, prd_id AS bar_prd_id FROM Product,
tblproduct WHERE name = prd_naam AND identificationCode <> '' ORDER BY
identificationCode
```

* Stock
```
INSERT INTO tblvoorraad (vrd_prd_id, vrd_datum, vrd_aantal, vrd_resterend,
vrd_stukprijs, vrd_btw) SELECT prd_id as vrd_prd_id, FROM_UNIXTIME(date) AS
vrd_datum, purchasedAmount AS vrd_aantal, currentAmount AS vrd_resterend,
ROUND(((Stock.price / purchasedAmount) * (1 + (margin / 100)) * (1 + (vatRate /
100))), 0) AS vrd_stukprijs, ROUND(((Stock.price / purchasedAmount) * (1 +
(margin / 100)) * (vatRate / 100)), 0) as vrd_btw FROM Product, tblproduct,
Stock WHERE product = idProduct AND prd_naam = name
```

--->8--- debug queries
select prd_id as vrd_prd_id, prd_naam, from_unixtime(date) as vrd_datum,
purchasedAmount as vrd_aantal, currentAmount as vrd_resterend, ((Stock.price /
purchasedAmount) * (1 + (margin / 100)) * (1 + (vatRate / 100))) as
vrd_stukprijs, ((Stock.price / purchasedAmount) * (1 + (margin / 100)) *
(vatRate / 100)) as vrd_btw from Product, tblproduct, Stock WHERE product =
idProduct and prd_naam = name

select prd_id as vrd_prd_id, prd_naam, from_unixtime(date) as vrd_datum,
purchasedAmount as vrd_aantal, currentAmount as vrd_resterend,
round(((Stock.price / purchasedAmount) * (1 + (margin / 100)) * (1 + (vatRate /
100))), 0) as vrd_stukprijs, round(((Stock.price / purchasedAmount) * (1 +
(margin / 100)) * (vatRate / 100)), 0) as vrd_btw, (Stock.price /
purchasedAmount) from Product, tblproduct, Stock WHERE product = idProduct and
prd_naam = name
---8<--- /debug
