CREATE DATABASE IF NOT EXISTS law_dev;
CREATE USER 'lawdev'@'%' IDENTIFIED BY 'lawdev';
GRANT ALL on law_dev.* TO 'lawdev'@'%';

CREATE DATABASE IF NOT EXISTS law_test ;
CREATE USER 'lawtest'@'%' IDENTIFIED BY 'lawtest';
GRANT ALL on law_test.* TO 'lawtest'@'%';

CREATE DATABASE IF NOT EXISTS law_adb_test ;
GRANT ALL on law_adb_test.* TO 'lawtest'@'%';

CREATE DATABASE IF NOT EXISTS law_sales;
CREATE USER 'law_sales'@'%' IDENTIFIED BY 'law_sales';
GRANT ALL on law_sales.* TO 'law_sales'@'%';

SELECT 'Setup DB: SUCCESS' AS '' ;
