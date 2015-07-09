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

Use law_sales;

CREATE TABLE `sales_order` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `subdomain` varchar(100) DEFAULT NULL,
  `volume` bigint(20) DEFAULT NULL,
  `ret_days` int(11) DEFAULT NULL,
  `plan_type` varchar(100) NOT NULL,
  `tier_name` varchar(100) DEFAULT NULL,
  `billing_channel` varchar(100) DEFAULT NULL,
  `effective_date` date NOT NULL,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;


