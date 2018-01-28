CREATE TABLE IF NOT EXISTS PhotoSharing
(imageid INTEGER PRIMARY KEY,
    remoteid LONGTEXT,
    CONSTRAINT PhotoSharing_Images FOREIGN KEY (imageid) REFERENCES Images (id) ON DELETE CASCADE ON UPDATE CASCADE)