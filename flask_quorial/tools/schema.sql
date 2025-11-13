/* SQLite syntax*/
/* last update 07 Maerz 23 */
/* syntax differs from univ lib in https://edu.dedisys.org/WBTServer/faces/main.jsp */

DROP TABLE IF EXISTS user;

CREATE TABLE IF NOT EXISTS "user" (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "Personen" (
	"PANr" NUMBER(5),
	"Vorname" TEXT(50)
		CONSTRAINT nn_Personen_Vorname NOT NULL,
	"Nachname" TEXT(50)
		CONSTRAINT nn_Personen_Nachname NOT NULL,
	"PLZ" NUMBER(5),
	"Ort" TEXT(10),
	"Strasse" TEXT(10),
	"HNr" NUMBER(3),
	"GebDatum" INTEGER
		CONSTRAINT nn_Personen_GebDatum NOT NULL,
	CONSTRAINT pk_Personen PRIMARY KEY (PANr)
);


CREATE Table IF NOT EXISTS "Pers_Telefon" (
	"PANr" NUMBER(5),
	"Telefon" TEXT(20),
	CONSTRAINT pk_Pers_Telefon PRIMARY KEY (PANr, Telefon),
	CONSTRAINT fk_Pers_Telefon_Personen FOREIGN KEY (PANr) REFERENCES Personen (PANr)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "Mitarbeiter"(
	"PANr" NUMBER(5),
	"AngNr" TEXT(20)
		CONSTRAINT unq_Mitarbeiter_AngNr UNIQUE
		CONSTRAINT nn_Mitarbeiter_AngNr NOT NULL,
	"Fachbereich" TEXT(20),
	"Gehalt" NUMBER(7),
	"Raum" NUMBER(3),
	"Einstellung" INTEGER,
	CONSTRAINT pk_Mitarbeiter PRIMARY KEY (PANr),
	CONSTRAINT fk_Mitarbeiter_Personen FOREIGN KEY (PANr) REFERENCES Personen (PANr)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS  "Lehrstuehle"(
	"Lehrstuhlbezeichnung" TEXT(50),
	"Anzahl_Planstellen" NUMBER(2)
		CONSTRAINT chk_Lehrstuehle_Anz_Planst CHECK (Anzahl_Planstellen >= 0),
	CONSTRAINT pk_Lehrstuehle PRIMARY KEY (Lehrstuhlbezeichnung)

);

CREATE TABLE IF NOT EXISTS "Professoren"(
	"PANr" NUMBER(5),
	"Lehrstuhlbezeichnung" TEXT(50)
		CONSTRAINT unq_Professoren_Lehrstuhlbez UNIQUE
		CONSTRAINT nn_Professoren_Lehrstuhlbez NOT NULL,
	"Stufe" TEXT(50)
		CONSTRAINT nn_Professoren_Stufe NOT NULL
		CONSTRAINT chk_Professoren_Stufe CHECK (Stufe IN ('C4', 'C3', 'C2', 'C1')),
	CONSTRAINT pk_Professoren PRIMARY KEY (PANr),
	CONSTRAINT fk_Professoren_Mitarbeiter FOREIGN KEY (PANr) REFERENCES Mitarbeiter (PANr)
		ON DELETE CASCADE,
	CONSTRAINT fk_Professoren_Lehrstuehle FOREIGN KEY (Lehrstuhlbezeichnung) 
		REFERENCES Lehrstuehle (Lehrstuhlbezeichnung)
);

CREATE TABLE IF NOT EXISTS "Studenten" (
	"PANr" NUMBER(5),
	"Matrikelnummer" TEXT(20)
		CONSTRAINT unq_Studenten_Matrikelnummer UNIQUE
		CONSTRAINT nn_Studenten_Matrikelnummer NOT NULL,
	"Studienfach" TEXT(20),
	"Immatrikulationsdatum" INTEGER
		CONSTRAINT nn_Studenten_Immatr_datum NOT NULL,
	CONSTRAINT pk_Studenten PRIMARY KEY (PANr),
	CONSTRAINT fk_Studenten_Personen FOREIGN KEY (PANr) REFERENCES Personen (PANr)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "Vorlesungen"(
	"V_Bezeichnung" TEXT(50),
	"SWS" NUMBER(2)
		CONSTRAINT chk_Vorlesungen_SWS CHECK (SWS > 0),
	"Semester" NUMBER(2)
		CONSTRAINT chk_Vorlesungen_Semester CHECK (Semester > 0),
	"Studiengang" TEXT(20),
	CONSTRAINT pk_Vorlesungen PRIMARY KEY (V_Bezeichnung)
);

CREATE TABLE IF NOT EXISTS "Verlage"(
	"Verlagsname" TEXT(30),
	"Verlagsort" TEXT(30),
	CONSTRAINT pk_Verlage PRIMARY KEY (Verlagsname)
);

CREATE TABLE IF NOT EXISTS "Buecher"(
	"ISBN" TEXT(20),
	"Titel" TEXT(100)
		CONSTRAINT nn_Buecher_Titel NOT NULL,
	"Verlagsname" TEXT(30)
		CONSTRAINT nn_Buecher_Verlagsname NOT NULL,
	CONSTRAINT pk_Buecher PRIMARY KEY (ISBN),
	CONSTRAINT fk_Buecher_Verlage FOREIGN KEY (Verlagsname) REFERENCES Verlage (Verlagsname)
);

CREATE TABLE IF NOT EXISTS "Buch_Autor" (
	"ISBN" TEXT(20),
	"Autor" TEXT(20),
	CONSTRAINT pk_Buch_Autor PRIMARY KEY (ISBN, Autor),
	CONSTRAINT fk_Buch_Autor_Buecher FOREIGN KEY (ISBN) REFERENCES Buecher (ISBN) 
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS  "Buch_Stichwort"
	(
	ISBN TEXT(20),
	Stichwort TEXT(20),
	CONSTRAINT pk_Buch_Stichwort PRIMARY KEY (ISBN, Stichwort),
	CONSTRAINT fk_Buch_Stichwort_Buecher FOREIGN KEY (ISBN) REFERENCES Buecher (ISBN) ON DELETE CASCADE
	);

CREATE TABLE IF NOT EXISTS  "Buch_Versionen"
	(
	ISBN TEXT(20),
	Auflage NUMBER(2),
	Jahr NUMBER(4)
			CONSTRAINT nn_Buch_Versionen_Jahr NOT NULL
			CONSTRAINT chk_Buch_Versionen_Jahr CHECK (Jahr >= 1800),
	Seiten NUMBER(4),
	Preis NUMBER
			CONSTRAINT chk_Buch_Versionen_Preis CHECK (Preis >= 0),
	CONSTRAINT pk_Buch_Versionen PRIMARY KEY (ISBN, Auflage),
	CONSTRAINT fk_Buch_Versionen_Buecher FOREIGN KEY (ISBN) REFERENCES Buecher (ISBN) ON DELETE CASCADE
	);

CREATE TABLE IF NOT EXISTS Buch_Exemplare
	(
	Inventarnr NUMBER(5),
	ISBN TEXT(20)
			CONSTRAINT nn_Buch_Exemplare_ISBN NOT NULL,
	Auflage NUMBER(2)
			CONSTRAINT nn_Buch_Exemplare_Auflage NOT NULL,
	CONSTRAINT pk_Buch_Exemplare PRIMARY KEY (Inventarnr),
	CONSTRAINT fk_Buch_Exemplare_Buch_Vers FOREIGN KEY (ISBN, Auflage) REFERENCES Buch_Versionen (ISBN, Auflage) ON DELETE CASCADE
	);

CREATE TABLE IF NOT EXISTS "Ausleihe" (
	"Inventarnr" NUMBER(5),
	"PANr" NUMBER(5)
		CONSTRAINT nn_Ausleihe_PANr NOT NULL,
	CONSTRAINT pk_Ausleihe PRIMARY KEY (Inventarnr),
	CONSTRAINT fk_Ausleihe_Buch_Exemplare FOREIGN KEY (Inventarnr) REFERENCES Buch_Exemplare (Inventarnr),
	CONSTRAINT fk_Ausleihe_Personen FOREIGN KEY (PANr) REFERENCES Personen (PANr)
);

CREATE TABLE IF NOT EXISTS "prueft" (
	"PANr" NUMBER(5),
	"Matrikelnummer" TEXT(20),
	"V_Bezeichnung" TEXT(20),
	"Note" NUMBER
		CONSTRAINT nn_prueft_Note NOT NULL
		CONSTRAINT chk_prueft_Note CHECK (Note BETWEEN 1 and 5),
	CONSTRAINT pk_prueft PRIMARY KEY (PANr, Matrikelnummer, V_Bezeichnung),
	CONSTRAINT fk_prueft_Professoren FOREIGN KEY (PANr) REFERENCES Professoren (PANr) 
		ON DELETE CASCADE,
	CONSTRAINT fk_prueft_Studenten FOREIGN KEY (Matrikelnummer) REFERENCES Studenten (Matrikelnummer),
	CONSTRAINT fk_prueft_Vorlesungen FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung)
);

CREATE TABLE IF NOT EXISTS "empfiehlt"(
	"PANr" NUMBER(5),
	"ISBN" TEXT(20),
	"V_Bezeichnung" TEXT(50),
	CONSTRAINT pk_empfiehlt PRIMARY KEY (PANr, ISBN, V_Bezeichnung),
	CONSTRAINT fk_empfiehlt_Professoren FOREIGN KEY (PANr) REFERENCES Professoren (PANr),
	CONSTRAINT fk_empfiehlt_Buecher FOREIGN KEY (ISBN) REFERENCES Buecher (ISBN),
	CONSTRAINT fk_empfiehlt_Vorlesungen FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung)
);

CREATE TABLE IF NOT EXISTS "Vorl_Voraus"(
	"V_Bezeichnung" TEXT(50),
	"Voraussetzung" TEXT(50),
	CONSTRAINT pk_Vorl_Voraus PRIMARY KEY (V_Bezeichnung, Voraussetzung),
	CONSTRAINT fk_Vorl_Voraus_Vorlesungen1 FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung)
		ON DELETE CASCADE,
	CONSTRAINT fk_Vorl_Voraus_Vorlesungen2 FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung) 
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "liest"(
	"PANr" NUMBER(5),
	"V_Bezeichnung" TEXT(50),
	"Semester" TEXT(10),
	CONSTRAINT pk_liest PRIMARY KEY (PANr, V_Bezeichnung),
	CONSTRAINT fk_liest_Professoren FOREIGN KEY (PANr) REFERENCES Professoren (PANr) 
		ON DELETE CASCADE,
	CONSTRAINT fk_liest_Vorlesungen FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "hoert"(
	"Matrikelnummer" TEXT(20),
	"V_Bezeichnung" TEXT(50),
	"Semester" NUMBER(2)
		CONSTRAINT chk_hoert_Semester CHECK (Semester > 0),
	CONSTRAINT pk_hoert PRIMARY KEY (Matrikelnummer, V_Bezeichnung),
	CONSTRAINT fk_hoert_Studenten FOREIGN KEY (Matrikelnummer) REFERENCES Studenten (Matrikelnummer)
		ON DELETE CASCADE,
	CONSTRAINT fk_hoert_Vorlesungen FOREIGN KEY (V_Bezeichnung) REFERENCES Vorlesungen (V_Bezeichnung)
		ON DELETE CASCADE
);

-- Chat functionality tables
CREATE TABLE IF NOT EXISTS "chat_sessions" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"user_id" INTEGER NOT NULL,
	"title" TEXT NOT NULL DEFAULT "New Chat",
	"created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	"updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_chat_sessions_user FOREIGN KEY (user_id) REFERENCES user (id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "chat_messages" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"session_id" INTEGER NOT NULL,
	"message" TEXT NOT NULL,
	"is_user" BOOLEAN DEFAULT TRUE,
	"timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_chat_messages_session FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
		ON DELETE CASCADE
);
