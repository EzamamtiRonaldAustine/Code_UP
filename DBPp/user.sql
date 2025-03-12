CREATE USER 'user1'@'localhost' IDENTIFIED BY 'password1';

ALTER USER 'user1'@'localhost' password EXPIRE;

ALTER USER 'user1'@'localhost' ACCOUNT LOCK;

ALTER USER 'user1'@'localhost' ACCOUNT UNLOCK;

ALTER USER 'user1'@'localhost' IDENTIFIED BY 'bag123';


