create_table_users = """
        CREATE TABLE IF NOT EXISTS users(
        telegram_id BIGINT PRIMARY KEY UNIQUE,
        first_name VARCHAR(40),
        last_name VARCHAR(40),
        balance REAL DEFAULT 0.0,
        state BOOLEAN DEFAULT TRUE
        );
        """