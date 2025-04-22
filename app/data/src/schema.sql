


CREATE TABLE fiction_mmsids(mmsid VARCHAR);
CREATE TABLE iso_639_3_SIL(Id VARCHAR, Part2b VARCHAR, Part2t VARCHAR, Part1 VARCHAR, "Scope" VARCHAR, Language_Type VARCHAR, Ref_Name VARCHAR, "Comment" VARCHAR);
CREATE TABLE languages(language_code VARCHAR, "language" VARCHAR, language_nob VARCHAR);
CREATE TABLE language_nob(language_code VARCHAR, "language" VARCHAR, language_nob VARCHAR);
CREATE TABLE translations(mmsid VARCHAR PRIMARY KEY, main_author VARCHAR, contributors VARCHAR[], translators VARCHAR[], title VARCHAR, subtitle VARCHAR, original_title VARCHAR, publisher VARCHAR, "language" VARCHAR, original_language VARCHAR, publication_year_str VARCHAR, publication_year_int INTEGER, ddc DOUBLE[], ddc800 BOOLEAN, ddc0 BOOLEAN);
CREATE TABLE urn_mmsid(urn VARCHAR, mmsid VARCHAR);
CREATE TABLE ol_first_editions(mmsid VARCHAR, work_key VARCHAR, edition_key VARCHAR, author VARCHAR, title VARCHAR, raw_publish_date VARCHAR, publish_year INTEGER, publishers VARCHAR[], publish_places_all VARCHAR[], publish_places VARCHAR, address VARCHAR, latitude DOUBLE, longitude DOUBLE, FOREIGN KEY (mmsid) REFERENCES translations(mmsid));


CREATE INDEX _mmsid_ ON urn_mmsid(mmsid);
CREATE INDEX _urn_ ON urn_mmsid(urn);


