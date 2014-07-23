CREATE DATABASE law_dev;
CREATE USER 'lawdev'@'%' IDENTIFIED BY 'lawdev';
GRANT ALL on law_dev.* TO 'lawdev'@'%';

CREATE USER 'lawtest'@'%' IDENTIFIED BY 'lawtest';
GRANT ALL on law_test.* TO 'lawtest'@'%';
