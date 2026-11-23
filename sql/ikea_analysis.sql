---check rows---

select count(*) as row_2009_2010 from dbo.[year 2009-2010];
select count(*) as row_2009_2010 from dbo.[year 2010-2011];


--comine both table useing union all---

select 
    Invoice, StockCode,Description,Quantity,
    COALESCE(
        TRY_CONVERT(datetime2, InvoiceDate, 120),
        TRY_CONVERT(datetime2, InvoiceDate, 105)
        ) As InvoiceDate,
        TRY_CONVERT(decimal(10,2), Price) AS Price,
        Customer_ID, Country, '2009-2010' AS SourceSheet
    INTO dbo.RetailCombined
    FROM dbo.[year 2009-2010]

    UNION ALL

    select 
    Invoice, StockCode,Description,Quantity,
    COALESCE(
        TRY_CONVERT(datetime2, InvoiceDate, 120),
        TRY_CONVERT(datetime2, InvoiceDate, 105)
        ) As InvoiceDate,
        TRY_CONVERT(decimal(10,2), Price) AS Price,
        Customer_ID, Country, '2009-2010' AS SourceSheet
    FROM dbo.[year 2010-2011]

    --- null handling---
SELECT COUNT(*) AS TOTAL_ROWS FROM dbo.RetailCombined
SELECT COUNT(*) AS Failed_Date FROM dbo.RetailCombined WHERE InvoiceDate is null;
SELECT COUNT(*) AS Failed_Price FROM dbo.RetailCombined WHERE Price is null;


---checking Customer_id is null---

select count(*) as missing_customer_id
from dbo.RetailCombined
where Customer_ID is null;

---check quenty is negitive or zero--

select count(*) as quentity_zero
from dbo.RetailCombined
where Quantity <=0;
 

 ---missing descripition ---
 select count(*) as missing_description
 from dbo.RetailCombined
 where Description is null;

 --extreing duplicates recordes--
 select Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer_ID,Country,
 count(*) as duplicates_recorders
 from dbo.RetailCombined
 GROUP BY Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer_ID,Country
 Having count(*) > 1;


--retaicleand table --
WITH Deduped AS (
     SELECT *,
        ROW_NUMBER() OVER(
            PARTITION BY Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer_ID,Country
            ORDER BY (SELECT NULL)
            ) AS RowNum
        FROM dbo.RetailCombined

)
SELECT Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer_ID,Country,SourceSheet
INTO dbo.RetailCleaned
From Deduped
Where RowNum =1;
