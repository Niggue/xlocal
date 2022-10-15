USE xlocal;

CREATE TABLE IF NOT EXISTS cryptocurrencies(
	currency_rank	INT(3)	NOT NULL PRIMARY KEY,
	symbol			CHAR(5)	NOT NULL,
	name			VARCHAR(15) NOT NULL,
	market_value	BIGINT NOT NULL,
	price 			INT NOT NULL
)

