-- Création de la base de données
CREATE DATABASE IF NOT EXISTS crawl_twitter CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE crawl_twitter;
SET default_storage_engine=InnoDB;


CREATE TABLE IF NOT EXISTS profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    twitter_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tweets (
    id VARCHAR(100),
    profile_id INT,
    content TEXT,
    publication_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_twitter_profile INT,
    INDEX idx_id (id),
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
) ENGINE=InnoDB;
