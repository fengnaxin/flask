import pymysql
from flask_migrate import Migrate, MigrateCommand
from flask import logging
from flask_script import Manager
from info import create_app, db

pymysql.install_as_MySQLdb()


#  创建工厂模式， 参数是develop或者production
app = create_app("develop")
# 创建角本对象
manger = Manager(app)

# 创建数据库迁移对象
Migrate(app, db)
manger.add_command("main", MigrateCommand)

if __name__ == '__main__':
    manger.run()
