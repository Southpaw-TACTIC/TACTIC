import tacticenv

# Run sql_convert for all supported database types
class SQLConvertAll(object):

    def convert_all(self):    
        from pyasm.search.upgrade.mysql import sql_convert
        m = sql_convert.MySQLConverter()
        m.convert_bootstrap()

        from pyasm.search.upgrade.oracle import sql_convert
        m = sql_convert.OracleConverter()
        m.convert_bootstrap()

        from pyasm.search.upgrade.sqlite import sql_convert
        m = sql_convert.SqliteConverter()
        m.convert_bootstrap()

        from pyasm.search.upgrade.sqlserver import sql_convert
        m = sql_convert.SQLServerConverter()
        m.convert_bootstrap()

if __name__ == '__main__':
    
    main = SQLConvertAll()
    main.convert_all()

