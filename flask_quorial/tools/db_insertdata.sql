/* SQLite syntax*/
/* last update 07 Maerz 23 */
/* syntax differs from univ lib in https://edu.dedisys.org/WBTServer/faces/main.jsp */

/*pw: Go4one! */
Insert into user (username, password) values ('1234', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa');
/*pw: Go4one! */
Insert into user (username, password) values ('2345', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa');
/*pw: Go4one! */
Insert into user (username, password) values ('3456', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa');
/*pw: Go4one! */
Insert into user (username, password) values ('7754', 'pbkdf2:sha256:260000$TE7rfiidZO86orwh$7e0f8049432d0ab7842f45e2d1de68ed3c61fbd01655ba9a5d093e350cf9edfa');
/*pw: Go4two! */
Insert into user (username, password) values ('6834', 'pbkdf2:sha256:260000$mpqrArAgux5YGorA$aeda075bfc2657fc7ff500ed15901e591ad81080920aa22121cb90ce758c855b');
/*pw: guest! */
Insert into user (username, password) values ('guest', 'pbkdf2:sha256:260000$MzkPXrPPnl7F5dN7$11fed544bf7be1e520e908eaaea1222d62e3b567b36853a68116b617ae75882f');


Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('1234','Max','Dre','96123','AL','BL','38','01.10.95');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('2345','Lunda','Lindt','96124','VT','RT','38','01.10.99');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('3456','Li','Li','96125','HD','ID','38','01.10.03');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('4711','Andreas','Heuer','18209','DBG','BHS','15','31.10.58');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('5588','Gunter','Saake','39106','MD','STS','55','05.10.60');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('6834','Michael','Korn','39104','MD','BS','41','24.09.74');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('7754','Andreas','Mueller','18209','DBR','RS','31','25.02.76');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('8832','Tamara','Jagellovsk','38106','BS','GS','12','11.11.73');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('9912','Antje','Hellhof','18059','HRO','AES','21','04.04.70');
Insert into PERSONEN (PANR,VORNAME,NACHNAME,PLZ,ORT,STRASSE,HNR,GEBDATUM) values ('9999','Christa','Loeser','96121','HD','TS','38','10.05.69');


Insert into PERS_TELEFON (PANR,TELEFON) values ('4711','0381-498-3401');
Insert into PERS_TELEFON (PANR,TELEFON) values ('4711','0381-498-3427');
Insert into PERS_TELEFON (PANR,TELEFON) values ('4711','038203-12230');
Insert into PERS_TELEFON (PANR,TELEFON) values ('5588','0391-345677');
Insert into PERS_TELEFON (PANR,TELEFON) values ('5588','0391-5592-3800');
Insert into PERS_TELEFON (PANR,TELEFON) values ('9999','06221-400177');


Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('4711','HRO-3447','Informatik','6000','209','01.03.94');
Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('5588','MD-5267','Informatik','6000','304','01.04.94');
Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('6834','MD-77185','Mathematik','750','309','01.09.94');
Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('7754','HRO-18532','Informatik','550','218','01.10.94');
Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('8832','MD-4567','Informatik','2800','302','01.08.94');
Insert into MITARBEITER (PANR,ANGNR,FACHBEREICH,GEHALT,RAUM,EINSTELLUNG) values ('9912','HRO-8134','Linguistik','2600','8','01.01.93');


Insert into LEHRSTUEHLE (LEHRSTUHLBEZEICHNUNG,ANZAHL_PLANSTELLEN) values ('Datenbank- und Informationssysteme','4');
Insert into LEHRSTUEHLE (LEHRSTUHLBEZEICHNUNG,ANZAHL_PLANSTELLEN) values ('Datenbanken und Informationssysteme','5');
Insert into LEHRSTUEHLE (LEHRSTUHLBEZEICHNUNG,ANZAHL_PLANSTELLEN) values ('Rechnernetze','2');


Insert into PROFESSOREN (PANR,LEHRSTUHLBEZEICHNUNG,STUFE) values ('4711','Datenbank- und Informationssysteme','C4');
Insert into PROFESSOREN (PANR,LEHRSTUHLBEZEICHNUNG,STUFE) values ('5588','Datenbanken und Informationssysteme','C4');


Insert into STUDENTEN (PANR,MATRIKELNUMMER,STUDIENFACH,IMMATRIKULATIONSDATUM) values ('1234','XY-951372','Informatik','01.10.95');
Insert into STUDENTEN (PANR,MATRIKELNUMMER,STUDIENFACH,IMMATRIKULATIONSDATUM) values ('2345','RS-992292','Informatik','01.10.99');
Insert into STUDENTEN (PANR,MATRIKELNUMMER,STUDIENFACH,IMMATRIKULATIONSDATUM) values ('3456','AY-031370','Informatik','01.10.03');
Insert into STUDENTEN (PANR,MATRIKELNUMMER,STUDIENFACH,IMMATRIKULATIONSDATUM) values ('6834','MD-891372','Informatik','01.10.89');
Insert into STUDENTEN (PANR,MATRIKELNUMMER,STUDIENFACH,IMMATRIKULATIONSDATUM) values ('7754','HRO-912291','Informatik','01.10.91');


Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Datenbanken I','4','5','Informatik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Datenbanken II','4','6','Informatik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Datenbanken','3','7','Mathematik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Objektorientierte Datenbanken','4','6','Informatik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Datenbanken fuer Ingenieure','2','7','Elektrotechnik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Verteilte Datenbanken','2','8','Informatik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Theorie relationaler Datenbanken','3','9','Informatik');
Insert into VORLESUNGEN (V_BEZEICHNUNG,SWS,SEMESTER,STUDIENGANG) values ('Spezifikationsmethoden','3','10','Informatik');


Insert into VERLAGE (VERLAGSNAME,VERLAGSORT) values ('Addison-Wesley','Bonn');
Insert into VERLAGE (VERLAGSNAME,VERLAGSORT) values ('Benjamin/Cummings','Redwood');
Insert into VERLAGE (VERLAGSNAME,VERLAGSORT) values ('Thomson','Bonn');


Insert into BUECHER (ISBN,TITEL,VERLAGSNAME) values ('3-89319-175-5','Das DB2-Handbuch','Addison-Wesley');
Insert into BUECHER (ISBN,TITEL,VERLAGSNAME) values ('0-8053-1753-8','Princ. Of DBS','Benjamin/Cummings');
Insert into BUECHER (ISBN,TITEL,VERLAGSNAME) values ('0-201-53771-0','Foundations of DB','Addison-Wesley');
Insert into BUECHER (ISBN,TITEL,VERLAGSNAME) values ('3-929821-31-1','Datenbanken','Thomson');


Insert into BUCH_AUTOR (ISBN,AUTOR) values ('0-201-53771-0','Abiteboul');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('0-201-53771-0','Hull');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('0-201-53771-0','Vianu');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('0-8053-1753-8','Elmasri');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('0-8053-1753-8','Navathe');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('3-89319-175-5','Vossen');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('3-89319-175-5','Witt');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('3-929821-31-1','Heuer');
Insert into BUCH_AUTOR (ISBN,AUTOR) values ('3-929821-31-1','Saake');


Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('0-201-53771-0','RDB');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('0-201-53771-0','Therie');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('0-8053-1753-8','ER');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('0-8053-1753-8','Lehrbuch');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('0-8053-1753-8','RDB');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('3-89319-175-5','RDB');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('3-929821-31-1','ER');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('3-929821-31-1','Lehrbuch');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('3-929821-31-1','OODB');
Insert into BUCH_STICHWORT (ISBN,STICHWORT) values ('3-929821-31-1','RDB');


Insert into BUCH_VERSIONEN (ISBN,AUFLAGE,JAHR,SEITEN,PREIS) values ('3-89319-175-5','1','1990','288','79');
Insert into BUCH_VERSIONEN (ISBN,AUFLAGE,JAHR,SEITEN,PREIS) values ('0-8053-1753-8','1','1989','802','72,35');
Insert into BUCH_VERSIONEN (ISBN,AUFLAGE,JAHR,SEITEN,PREIS) values ('0-8053-1753-8','2','1994','873','88,58');
Insert into BUCH_VERSIONEN (ISBN,AUFLAGE,JAHR,SEITEN,PREIS) values ('0-201-53771-0','1','1995','685','87,45');
Insert into BUCH_VERSIONEN (ISBN,AUFLAGE,JAHR,SEITEN,PREIS) values ('3-929821-31-1','1','1995','500','79');


Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('1','3-89319-175-5','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('5','0-8053-1753-8','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('84','0-8053-1753-8','2');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('85','0-8053-1753-8','2');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('101','0-201-53771-0','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('102','0-201-53771-0','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('138','3-929821-31-1','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('139','3-929821-31-1','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('140','3-929821-31-1','1');
Insert into BUCH_EXEMPLARE (INVENTARNR,ISBN,AUFLAGE) values ('141','3-929821-31-1','1');


Insert into AUSLEIHE (INVENTARNR,PANR) values ('1','1234');
Insert into AUSLEIHE (INVENTARNR,PANR) values ('140','7754');
Insert into AUSLEIHE (INVENTARNR,PANR) values ('141','4711');
Insert into AUSLEIHE (INVENTARNR,PANR) values ('101','2345');
Insert into AUSLEIHE (INVENTARNR,PANR) values ('102','3456');
Insert into AUSLEIHE (INVENTARNR,PANR) values ('85','6834');


Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','HRO-912291','Datenbanken I','2');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','HRO-912291','Objektorientierte Datenbanken','3');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('5588','MD-891372','Datenbanken I','1');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('5588','MD-891372','Spezifikationsmethoden','2');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('5588','XY-951372','Datenbanken I','1');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('5588','RS-992292','Spezifikationsmethoden','3');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('5588','AY-031370','Datenbanken I','3');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','HRO-912291','Theorie relationaler Datenbanken','1');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','HRO-912291','Spezifikationsmethoden','4');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','HRO-912291','Datenbanken II','1');
Insert into PRUEFT (PANR,MATRIKELNUMMER,V_BEZEICHNUNG,NOTE) values ('4711','MD-891372','Datenbanken I','1');


Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('4711','0-201-53771-0','Theorie relationaler Datenbanken');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('4711','0-8053-1753-8','Datenbanken I');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('4711','0-8053-1753-8','Datenbanken II');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('4711','3-929821-31-1','Datenbanken I');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('5588','0-8053-1753-8','Datenbanken I');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('5588','0-8053-1753-8','Datenbanken II');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('5588','3-89319-175-5','Datenbanken fuer Ingenieure');
Insert into EMPFIEHLT (PANR,ISBN,V_BEZEICHNUNG) values ('5588','3-929821-31-1','Datenbanken I');


Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Datenbanken II','Datenbanken I');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Objektorientierte Datenbanken','Datenbanken I');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Spezifikationsmethoden','Objektorientierte Datenbanken');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Spezifikationsmethoden','Theorie relationaler Datenbanken');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Theorie relationaler Datenbanken','Datenbanken I');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Verteilte Datenbanken','Datenbanken II');
Insert into VORL_VORAUS (V_BEZEICHNUNG,VORAUSSETZUNG) values ('Verteilte Datenbanken','Objektorientierte Datenbanken');


Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('4711','Datenbanken I','WS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('4711','Theorie relationaler Datenbanken','WS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('4711','Datenbanken II','SS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('4711','Objektorientierte Datenbanken','SS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('5588','Datenbanken fuer Ingenieure','WS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('5588','Datenbanken I','WS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('5588','Verteilte Datenbanken','SS');
Insert into LIEST (PANR,V_BEZEICHNUNG,SEMESTER) values ('5588','Spezifikationsmethoden','SS');


Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('MD-891372','Datenbanken I','5');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('MD-891372','Spezifikationsmethoden','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('MD-891372','Verteilte Datenbanken','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('HRO-912291','Datenbanken I','5');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('HRO-912291','Objektorientierte Datenbanken','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('HRO-912291','Datenbanken II','8');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('RS-992292','Objektorientierte Datenbanken','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('RS-992292','Datenbanken II','8');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('XY-951372','Spezifikationsmethoden','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('XY-951372','Datenbanken II','8');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('AY-031370','Spezifikationsmethoden','6');
Insert into HOERT (MATRIKELNUMMER,V_BEZEICHNUNG,SEMESTER) values ('AY-031370','Datenbanken I','5');
