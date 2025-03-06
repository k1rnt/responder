-- seed.sql
DROP TABLE IF EXISTS log;
DROP TABLE IF EXISTS route;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE route (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(255) NOT NULL UNIQUE,
    response_headers TEXT,
    response_body TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    remote_addr VARCHAR(255),
    method VARCHAR(10),
    query_params TEXT,
    FOREIGN KEY (route_id) REFERENCES route(id)
);

-- 例として "secret" のハッシュ値（Werkzeug の generate_password_hash('secret') により生成）
INSERT INTO user (username, password)
VALUES ('admin', 'scrypt:32768:8:1$jUdneWqnX01V4g6j$108f51e620814e811e439672807813644e99a8b551be7b9a89ce24b13e6ff3f608f71fa268b091a076866d0637308f21d79a91bcda43ab1ba769e5b739d56e4b');
