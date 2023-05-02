from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

# create a database connection
db = QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName('mydatabase.db')
if not db.open():
    print('Unable to establish a database connection')
    exit(1)

# create a QSqlQueryModel and set the SQL query
model = QSqlQueryModel()
query = QSqlQuery()
query.prepare('SELECT * FROM mytable')
if not query.exec():
    print('Unable to execute query')
    exit(1)
model.setQuery(query)
