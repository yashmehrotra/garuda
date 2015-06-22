-- users ( user_id, user_email,user_name,user_password,user_handle,user_bio)
-- tags ( tag_id, tag_value,user_tweet_id)
-- The other tables will generated automatically

CREATE DATABASE garuda;
USE garuda;

CREATE TABLE users ( 
    user_id int PRIMARY KEY AUTO_INCREMENT,
    user_email varchar(500),
    user_name varchar(500),
    user_password varchar(500),
    user_handle varchar(500),
    user_bio varchar(500)
);

CREATE TABLE tags (
    tag_id int PRIMARY KEY AUTO_INCREMENT,
    tag_value varchar(500),
    user_tweet_id varchar(1000)
);
