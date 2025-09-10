
# Allow Django to use PyMySQL as MySQLdb (pure Python, easier to install)
try:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()
except Exception:
    # If pymysql isn't installed yet, ignore. Django will still run on sqlite for dev.
    pass
