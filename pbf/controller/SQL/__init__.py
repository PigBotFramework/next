class SQL:
    def __init__(self, driver) -> None:
        self.driver = driver

    def execute(self, sql: str, params: tuple = ()) -> list:
        cursor = self.driver.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def commit(self):
        self.driver.commit()

    def close(self):
        self.driver.close()

    def __del__(self):
        self.commit()
        # self.close()
