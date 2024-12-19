DROP TABLE IF EXISTS jourSemaine CASCADE;
DROP TABLE IF EXISTS gerant CASCADE;
DROP TABLE IF EXISTS employe CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS magasin CASCADE;
DROP TABLE IF EXISTS facture CASCADE;
DROP TABLE IF EXISTS contient CASCADE;
DROP TABLE IF EXISTS vend CASCADE;
DROP TABLE IF EXISTS detailfact CASCADE;
DROP TABLE IF EXISTS projet CASCADE;
DROP TABLE IF EXISTS travaille CASCADE;
DROP TABLE IF EXISTS composant CASCADE;



-- Table for days of the week
CREATE TABLE jourSemaine (
    jour VARCHAR(10) PRIMARY KEY
);

-- Insert days of the week
INSERT INTO jourSemaine VALUES ('Lundi'), ('Mardi'), ('Mercredi'), ('Jeudi'), 
                               ('Vendredi'), ('Samedi'), ('Dimanche');


-- Table for managers
CREATE TABLE gerant (
    idGer SERIAL PRIMARY KEY,
    nomGer VARCHAR(50) NOT NULL,
    prenomGer VARCHAR(50) NOT NULL,
    mailGer VARCHAR(50) UNIQUE,
    telGer VARCHAR(16),
    mdpGer VARCHAR(500) NOT NULL
);

-- Insert  managers
INSERT INTO gerant (nomGer, prenomGer, mailGer, telGer, mdpGer) VALUES
    ('Dupont', 'Jean', 'dupontjean@sqlmail.com', '+33648099825', '$2b$12$zqRYR/3BakzvnlKThS5/K.D8MRjHC4dQhDpclOwErbaZDBZR5/E32'), -- mdpGerant1
    ('Durand', 'Pierre', 'durantpierre@sqlmail.com', '+33728904322', '$2b$12$.PZbuh5px1tyMSxILbWuAORTnOMlHTzykDQ03bnk0lSSPWgygtbam'), -- mdpGerant2
    ('Martin', 'Cecile', 'martincecile@sqlmail.com', '+33751851171', '$2b$12$zhSd9GifYzqM3WK5D.AMJ.mTFY690twSay9DAgQ3DrVSmbzfHj8tO'), -- mdpGerant3
    ('Lefevre', 'Jacques', 'lefevrejacques@sqlmail.com', '+33799470795', '$2b$12$K.PkEsfcG5ac4AIkfKVxd.rwGfrwI1ZAfI0q1bNYBHiey825jSHSS'), -- mdpGerant4
    ('Leroy', 'Marie', 'leroymarie@sqlmail.com', '+33663818723', '$2b$12$QgwGXU.ULV9Tska/F5h/4uLE3ub7GywZ8CcDIVINZXDEX2pGcbQnK'); -- mdpGerant5


-- Table for employees
CREATE TABLE employe (
    idEmp SERIAL PRIMARY KEY,
    nomEmp VARCHAR(50) NOT NULL,
    prenomEmp VARCHAR(50) NOT NULL,
    mailEmp VARCHAR(50) UNIQUE,
    telEmp VARCHAR(16),
    mdpEmp VARCHAR(500) NOT NULL
);

-- Insert  employees
INSERT INTO employe (nomEmp, prenomEmp, mailEmp, telEmp, mdpEmp) VALUES
    ('Mosco', 'Prisca', 'moscoprisca@sqlmail.com', '+33694685904', '$2b$12$UnLNvVryMaRJehkuwo4q/egjDEMgU9RaAJT5O2wz1zYNHYvhzmaoe'), -- mdpEmploye1
    ('Verstappen', 'Max', 'maxverstappen@sqlmail.com', '+33716119349', '$2b$12$7TAGXZE1Yhxn2cwot0eZj.wZJSqm5UJPTlvRa800aEBtI2e0pEJTi'), -- mdpEmploye2
    ('Gasly', 'Pierre', 'gaslypierre@sqlmail.com', '+33619513055', '$2b$12$QPwwSOc8pODYQLg8Zb5fY.aBvPR.xJuZtfF3zGagRh8I7ImBNjMT2'), -- mdpEmploye3
    ('Ocon', 'Esteban', 'oconesteban@sqlmail.com', '+33700978736', '$2b$12$Vbch5ENAnRR5DuRbftkORu0wmEaC.S5WsiDo9wcwyJO3YSqYt8ioi'), -- mdpEmploye4
    ('Conway', 'Mike', 'conwaymike@sqlmail.com', '+33768256008', '$2b$12$eMEbg167vPTzmralRvMroeXbPK/ZwFM0fskyZv280gm3Am.dZet5C'); -- mdpEmploye5


-- Table for stores
CREATE TABLE magasin (
    idMag SERIAL PRIMARY KEY,
    nomMag VARCHAR(50) NOT NULL,
    adresseMag VARCHAR(50) UNIQUE,
    telMag VARCHAR(16) UNIQUE,
    idGer INT UNIQUE,
    FOREIGN KEY (idGer) REFERENCES gerant(idGer) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Insert  stores
INSERT INTO magasin (nomMag, adresseMag, telMag, idGer) VALUES
    ('HP', '10 rue de Rivoli, 75001 Paris, France', '+33686650459', 1),
    ('Dell', '25 avenue des Champs Elysees, 75008 Paris, France', '+33634796399', 2),
    ('Asus', '18 boulevard Victor Hugo, 35000 Rennes, France', '+33669922638', 3);


-- Table for clients
CREATE TABLE client (
    idCli SERIAL PRIMARY KEY,
    nomCli VARCHAR(50) NOT NULL,
    prenomCli VARCHAR(50) NOT NULL,
    mailCli VARCHAR(50) UNIQUE,
    telCli VARCHAR(16),
    mdpCli VARCHAR(500) NOT NULL
);

-- Insert  clients
INSERT INTO client (nomCli, prenomCli, mailCli, telCli, mdpCli) VALUES
    ('Shetty', 'Jey', 'shettyjey@sqlmail.com', '+81753816382', '$2b$12$L2bCy6JkX7skU2W.FEquEekyvZuiLrV2N9Y0p8ZWynZVLPy8NRUCS'), -- mdpClient1
    ('Gomez', 'Selena', 'gomezselena@sqlmail.com', '+213687588243', '$2b$12$7YTC.kMoqJ1hWDN7yiDYFuxQAaLhHC0UAP84fd.9MWbqSnyf/wuK2'), -- mdpClient2
    ('Monkey', 'Luffy', 'monkeyluffy@sqlmail.com', '+213664037234', '$2b$12$u4LSaZo.kfe7WodZt45YzuPF85I9T02tzCC7KYtG5ms3cPsJqIkGy'), -- mdpClient3
    ('Dragneel', 'Happy', 'dragneelhappy@sqlmail.com', '+81601536143', '$2b$12$eZOySzHZrWWuQzo4yTbSDunbWQDy40RCdKGTz00Qy6cTUKe3Xxh5W'); -- mdpClient4


-- Table for components
CREATE TABLE composant (
    idComp SERIAL PRIMARY KEY,
    nomComp VARCHAR(50) NOT NULL,
    descriptionComp VARCHAR(100) NOT NULL,
    marqueComp VARCHAR(50) NOT NULL
);

-- Insert  components
INSERT INTO composant (nomComp, descriptionComp, marqueComp) VALUES
    ('Keyboard', 'Mechanical keyboard', 'Asus'),
    ('Mouse', 'Wireless mouse', 'HP'),
    ('Charger', 'Laptop charger', 'Dell'),
    ('Battery', 'Laptop battery', 'HP'),
    ('Graphic card', 'Nvidia Card', 'Nvidia');


-- Table for projects
CREATE TABLE projet (
    idProj SERIAL PRIMARY KEY,
    nomProj VARCHAR(50) NOT NULL,
    idCli INT,
    FOREIGN KEY (idCli) REFERENCES client(idCli) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT unique_proj_client UNIQUE (idCli, nomProj)
);

-- Insert  projects
INSERT INTO projet (nomProj, idCli) VALUES
    ('Keyboards to buy', 1),
    ('Mouse i like', 1),
    ('Components for friend', 2),
    ('Like lists', 3),
    ('Present', 2),
    ('Maybe', 1),
    ('Computer set', 3),
    ('Laptop Upgrade', 1),  -- Projet 1, Client 1
    ('Office Setup', 2),    -- Projet 2, Client 2
    ('Friend PC', 3),    -- Projet 3, Client 3
    ('Gamer Setup', 4),  -- Projet 4, Client 4
    ('Business PC', 1);     -- Projet 5, Client 1


-- Table for invoices (factures)
CREATE TABLE facture (
    idFact SERIAL PRIMARY KEY,
    dateAchat DATE NOT NULL,
    idEmp INT,
    idCli INT,
    idMag INT,
    FOREIGN KEY (idEmp) REFERENCES employe(idEmp) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (idCli) REFERENCES client(idCli) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (idMag) REFERENCES magasin(idMag) ON DELETE CASCADE ON UPDATE CASCADE

);

-- Insert  invoices
INSERT INTO facture (dateAchat, idEmp, idCli, idMag) VALUES
    ('2020-10-10', 1, 1, 1),
    ('2020-11-10', 1, 1, 2),
    ('2020-09-10', 2, 2, 2),
    ('2020-08-10', 2, 2, 1),
    ('2020-05-10', 3, 3, 1),
    ('2021-05-10', 1, 1, 1),  -- Employé 1, Client 1, Magasin 1
    ('2021-06-12', 2, 3, 2),  -- Employé 2, Client 3, Magasin 2
    ('2022-03-25', 3, 4, 1),  -- Employé 3, Client 4, Magasin 1
    ('2022-04-15', 4, 2, 2),  -- Employé 4, Client 2, Magasin 2
    ('2023-01-20', 5, 1, 3),  -- Employé 5, Client 1, Magasin 3
    ('2023-05-10', 3, 3, 1),
    ('2024-04-29', 5, 1, 1);
    


-- Table for work schedule
CREATE TABLE travaille (
    jour VARCHAR(10),
    idEmp INT,
    idMag INT,
    PRIMARY KEY (jour, idEmp, idMag),
    FOREIGN KEY (jour) REFERENCES jourSemaine(jour),
    FOREIGN KEY (idEmp) REFERENCES employe(idEmp) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (idMag) REFERENCES magasin(idMag) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Insert  work schedule data
INSERT INTO travaille (jour, idEmp, idMag) VALUES
    ('Lundi', 1, 1), ('Mardi', 1, 2), ('Mercredi', 1, 3),
    ('Lundi', 2, 1), ('Jeudi', 2, 1), ('Vendredi', 2, 1),
    ('Lundi', 3, 3), ('Mardi', 3, 3);


-- Table for vend (store selling components)
CREATE TABLE vend (
    idMag INT,
    idComp INT,
    prixUnit FLOAT,
    stock INT DEFAULT 0,
    PRIMARY KEY (idMag, idComp),
    FOREIGN KEY (idMag) REFERENCES magasin(idMag) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idComp) REFERENCES composant(idComp) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT reductionComp_pos check (prixUnit > 0)

);

-- Insert vend data
INSERT INTO vend (idMag, idComp, prixUnit, stock) VALUES
    (1, 1, 20, 20), (1, 2, 20, 20), (2, 1, 20, 20), (2, 2, 20, 20), 
    (1, 5, 50, 20),
    (2, 3, 40, 20),   -- Magasin 2, Composant 3 (Charger)
    (2, 4, 60, 15),   -- Magasin 2, Composant 4 (Battery)
    (3, 5, 100, 10);  -- Magasin 3, Composant 5 (Graphic Card)


-- Table for detailfact (invoice details)
CREATE TABLE detailfact (
    idFact INT,
    idComp INT,
    quantite INT NOT NULL,
    reductionComp INT NOT NULL,
    PRIMARY KEY (idFact, idComp),
    FOREIGN KEY (idFact) REFERENCES facture(idFact) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idComp) REFERENCES composant(idComp) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT reductionComp_pos check (reductionComp >= 0)

);

-- Insert  detailfact data
INSERT INTO detailfact (idFact, idComp, quantite, reductionComp) VALUES
    (1, 1, 2, 40),  -- 2 Keyboards in Invoice 1 at 40 each
    (1, 2, 1, 30),  -- 1 Mouse in Invoice 1 at 30
    (2, 3, 3, 50),  -- 3 Chargers in Invoice 2 at 50
    (6, 5, 1, 50),
    (3, 4, 2, 15),  -- Facture 3, Composant 4 (Battery), Quantité 2, Réduction 15%
    (4, 5, 1, 20);  -- Facture 4, Composant 5 (Graphic Card), Quantité 1, Réduction 20%

-- Table for contient (project contents)
CREATE TABLE contient (
    idProj INT,
    idComp INT,
    quantite INT NOT NULL,
    PRIMARY KEY (idProj, idComp),
    FOREIGN KEY (idProj) REFERENCES projet(idProj) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idComp) REFERENCES composant(idComp) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Insert  contient data
INSERT INTO contient (idProj, idComp, quantite) VALUES
    (1, 1, 5),  -- 5 Keyboards in Project 1
    (2, 2, 3),  -- 3 Mice in Project 2
    (3, 3, 2),  -- 2 Chargers in Project 3
    (3, 4, 1);  -- 1 Battery in Project 3

-- View for the most loyal customer
CREATE VIEW clientFidele AS (
SELECT c.nomCli, c.prenomCli, c.mailCli
FROM client AS c
JOIN facture AS f ON c.idCli = f.idCli
JOIN detailfact AS dt ON f.idFact = dt.idFact
JOIN composant AS cp ON dt.idComp = cp.idComp
WHERE cp.marqueComp = 'HP'
GROUP BY c.idCli
ORDER BY SUM(dt.quantite) DESC
LIMIT 1);

-- View for potential customers
CREATE VIEW futursAcheteurs AS(
SELECT client.nomCli, client.prenomCli, client.mailCli FROM client EXCEPT 
SELECT c.nomCli, c.prenomCli, c.mailCli
FROM client AS c
JOIN facture AS f ON c.idCli = f.idCli
JOIN detailfact AS dt ON f.idFact = dt.idFact
JOIN composant AS cp ON dt.idComp = cp.idComp
WHERE cp.nomComp = 'Graphic card' AND f.dateAchat >= CURRENT_DATE - INTERVAL '2 years'
);
