CREATE TABLE IF NOT EXISTS users (
	id SERIAL NOT NULL,
	email VARCHAR NOT NULL,
	password VARCHAR NOT NULL,
	full_name VARCHAR NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
);


CREATE TABLE IF NOT EXISTS admins (
	id SERIAL NOT NULL,
	email VARCHAR NOT NULL,
	password VARCHAR NOT NULL,
	full_name VARCHAR NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (email)
);


CREATE TABLE IF NOT EXISTS bank_accounts (
	id SERIAL NOT NULL,
	account_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	balance INTEGER NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (account_id),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
	id SERIAL NOT NULL,
	transaction_id VARCHAR NOT NULL,
	account_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	amount INTEGER NOT NULL,
	signature VARCHAR NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (transaction_id),
	FOREIGN KEY(account_id) REFERENCES bank_accounts (account_id) ON DELETE CASCADE,
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);