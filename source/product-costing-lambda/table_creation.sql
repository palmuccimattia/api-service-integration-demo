USE api_connector_demo;

CREATE TABLE Margherita (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Alici (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Alici FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Amatriciana (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Pomodorini FLOAT,
    Cipolla FLOAT,
    Pancetta FLOAT,
    GranaPadano FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Capricciosa (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Funghi FLOAT,
    Carciofi FLOAT,
    ProsciuttoCotto FLOAT,
    Olive FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Carciofi (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Carciofi FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Cipolla (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Cipolla FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE CottoScamorza (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Scamorza FLOAT,
    GranaPadano FLOAT,
    ProsciuttoCotto FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE CrudoRucolaGranaStracciatella (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Stracciatella FLOAT,
    ProsciuttoCrudo FLOAT,
    Rucola FLOAT,
    GranaPadanoExtra FLOAT,
    Pomodorini FLOAT,
    Olio_d_oliva FLOAT,
    AcetoBalsamico FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE CrudoRucolaGrana (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    ProsciuttoCrudo FLOAT,
    Rucola FLOAT,
    GranaPadanoExtra FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE FunghiBianca (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Funghi FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE FunghiCotto (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Funghi FLOAT,
    ProsciuttoCotto FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE FunghiSalsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Salsiccia FLOAT,
    Mozzarella FLOAT,
    Funghi FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Funghi (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Funghi FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Grasselli (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Grasselli FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Ortolana (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Melanzane FLOAT,
    Patate FLOAT,
    Zucchine FLOAT,
    Pomodorini FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Parmigiana (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Melanzane FLOAT,
    Pomodorini FLOAT,
    Salsiccia FLOAT,
    GranaPadano FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE PatateCotto (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    ProsciuttoCotto FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE PatatePancetta (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    Pancetta FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE PatatePorcini (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    FunghiMisti FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE PatateSalsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    Salsiccia FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE PatateWurstel (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    Wurstel FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Patate (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Patate FLOAT,
    Mozzarella FLOAT,
    GranaPadano FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Piccante (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Salame FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Pomodoro (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE QuattroFormaggi (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Scamorza FLOAT,
    Bergader FLOAT,
    GranaPadano FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Rosmarino (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Rosmarino FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE SalsaRosaGamberetti (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Maionese FLOAT,
    Ketchup FLOAT,
    Pomodorini FLOAT,
    Rucola FLOAT,
    Gamberetti FLOAT,
    Olive FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Salsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Salsiccia FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Peperoni (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Peperoni FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE SpinaciSalsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Spinaci FLOAT,
    Salsiccia FLOAT,
    GranaPadano FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Sushi (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Stracciatella FLOAT,
    Zucchine FLOAT,
    Pomodorini FLOAT,
    Olive FLOAT,
    Gamberetti FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Tartufata (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Stracciatella FLOAT,
    CremaTartufo FLOAT,
    Carciofi FLOAT,
    FunghiMisti FLOAT,
    Rucola FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE TartufoPorcini (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    CremaTartufo FLOAT,
    FunghiMisti FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE TartufoSalsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    CremaTartufo FLOAT,
    Mozzarella FLOAT,
    Salsiccia FLOAT,
    GranaPadano FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE TonnoPomodoriniRucola (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Pomodorini FLOAT,
    Tonno FLOAT,
    Rucola FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Vegana (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Melanzane FLOAT,
    Zucchine FLOAT,
    Pomodorini FLOAT,
    Carciofi FLOAT,
    Olive FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Wurstel (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Pomodoro FLOAT,
    Mozzarella FLOAT,
    Wurstel FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE ZucchineCotto (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Zucchine FLOAT,
    ProsciuttoCotto FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE ZucchinePancetta (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Zucchine FLOAT,
    Pancetta FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE ZucchinePomodorini (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Zucchine FLOAT,
    Pomodorini FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE ZucchineSalsiccia (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Zucchine FLOAT,
    Salsiccia FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);

CREATE TABLE Zucchine (
    Data DATE,
    Farina FLOAT,
    Olio FLOAT,
    Sale FLOAT,
    Zucchero FLOAT,
    Lievito FLOAT,
    Mozzarella FLOAT,
    Zucchine FLOAT,
    Olio_d_oliva FLOAT,
    Totale_CV FLOAT,
    Totale_CF_Manodopera FLOAT,
    Totale_CF_Generali FLOAT,
    CostoPizza FLOAT,
    PrezzoPizza FLOAT
);