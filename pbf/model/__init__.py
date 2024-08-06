try:
    from ..controller import Cache
    from ..config import sql_driver
except ImportError:
    from pbf.controller import Cache
    from pbf.config import sql_driver


class ModelBase:
    sql_update: str = "UPDATE `{}` SET {} WHERE {}"
    sql_insert: str = "REPLACE INTO `{}` ({}) VALUES {}"
    sql_delete: str = "DELETE FROM `{}` WHERE {}"
    sql_createTable: str = "CREATE TABLE IF NOT EXISTS `{}`({})"
    sql_dropTable: str = "DROP TABLE IF EXISTS `{}`"
    sql_select: str = "SELECT * FROM `{}`"
    sql_whereCase: str = ""
    sql_whereList: list = []

    db_table: str = None
    db_prefix: str = "bot_"
    col: list = []

    format_insert: list = []
    format_update: list = []
    format_createTable: list = []

    def __str__(self):
        return f'<pbf.model.ModelBase {self.db_table}>'

    def _getTableName(self):
        return self.db_prefix + self.db_table

    def _c(self):
        return "db_" + self._getTableName()

    def _dropTable(self):
        sql_driver.execute(self.sql_dropTable.format(self._getTableName()))
        sql_driver.commit()
        self.delFlag = True
        del self
        return None

    def _sync(self):
        self.__insert()
        self.__update()
        self.__delete()

    def _getCol(self):
        self.col = []
        for i in dir(self):
            if i[0:1] == "_" or not callable(getattr(self, i)):
                continue
            name = i
            i = getattr(self, i)
            desc = i.__doc__
            default = i()
            if isinstance(default, tuple) or isinstance(default, list):
                default = default[0]
            _type = type(name)
            self.col.append({
                "desc": desc,
                "name": name,
                "default": f"`{name}` {default}",
                "type": _type
            })

    def __update(self):
        pass

    def __insert(self):
        pass

    def __delete(self):
        pass


class DictModel(ModelBase):
    map: list = []
    args: dict = {}
    exists: bool = True
    cache: dict = {}
    delFlag: bool = False
    format_delete: bool = False

    def _sync(self):
        self.__insert()
        self.__update()
        self.__delete()

    def _getIndexStr(self, i):
        ret_str: str = f"['{self._c()}']"
        if Cache.cacheList.get(self._c()) is None:
            Cache.cacheList[self._c()] = dict()
        map_list: list = self.map
        obj = Cache.cacheList.get(self._c())
        for item in map_list:
            ob = i.get(item)
            ret_str += f"[\"{ob}\"]"
            obj = obj.get(str(i.get(item)))
            if obj is None:
                exec(f"Cache.cacheList{ret_str} = dict()")
                obj = {}

        return ret_str

    def __init__(self, **kwargs):
        # Init class vars.
        for i in dir(self):
            if i[0:1] == "_" or callable(getattr(self, i)):
                continue
            var_type = type(getattr(self, i))
            setattr(self, i, var_type(getattr(self, i)))

        self.args = kwargs

        # 初始化数据
        self._getCol()
        self._refresh(insert_flag=True, kwargs=kwargs)
        self._refreshWhereCase()

    def __del__(self):
        if not self.delFlag:
            self._sync()

    def _refreshWhereCase(self):
        # 生成where子句
        self.sql_whereCase = ""
        self.sql_whereList = []

        flag: bool = False
        for i in self.map:
            if flag:
                self.sql_whereCase += " AND "
            else:
                flag = True
            self.sql_whereCase += "`{}` = ?".format(i)
            self.sql_whereList.append(self.args.get(i))

    def _createTable(self, refresh_cache=True):
        sql_str: str = ""
        flag: bool = False
        sql_list: list = self.col + self.format_createTable

        for i in sql_list:
            if flag:
                sql_str += ", "
            else:
                flag = True
            if isinstance(i, dict):
                sql_str += i.get("default")
            elif isinstance(i, str):
                sql_str += i
        sql = self.sql_createTable.format(self._getTableName(), sql_str)
        sql_driver.execute(sql)
        sql_driver.commit()

        if refresh_cache is True:
            self.cache = {}
            Cache.set(self._c(), {})

            sql = self.sql_select.format(self._getTableName())
            data = sql_driver.execute(sql)
            for i in data:
                sql_str = self._getIndexStr(i)
                exec(f"Cache.cacheList{sql_str} = dict(i)")
            return self

    def _get(self, key: str, default=None, *args, **kwargs):
        data = self.cache.get(key, *args, **kwargs)
        if data is None and default is None:
            _default = getattr(self, key)()
            if isinstance(_default, tuple) or isinstance(_default, list):
                default = _default[1]
        return data if data is not None else default

    def _getAll(self):
        return self.cache

    def _insert(self, **kwargs):
        # 在缓存中新增
        idx_str = self._getIndexStr(kwargs)
        exec(f"Cache.cacheList{idx_str} = dict(kwargs)")

        self.exists = True
        self.delFlag = False
        self.cache = kwargs
        self.args = kwargs
        self._refreshWhereCase()

        # 更新到同步列表
        insert_list: list = []
        for i in self.col:
            v = kwargs.get(i.get('name'))
            if v is None:
                _v = getattr(self, i.get('name'))()
                if isinstance(_v, tuple) or isinstance(_v, list):
                    v = _v[1]
            insert_list.append(v)
        self.format_insert.append(insert_list)
        return self

    def _delete(self):
        # 缓存删除
        idx_str = self._getIndexStr(self.args)
        exec(f"del Cache.cacheList{idx_str}")

        self.format_delete = True

        return self

    def __delete(self):
        # 数据库删除
        if self.format_delete:
            sql_driver.execute(
                self.sql_delete.format(self._getTableName(), self.sql_whereCase),
                tuple(self.sql_whereList)
            )
            sql_driver.commit()
            self.format_delete = False
        else:
            return False

    def _set(self, **kwargs):
        for k, v in kwargs.items():
            self.format_update.append({
                "key": k,
                "value": v
            })

            # 修改缓存
            '''
            _cache = Cache.cacheList
            cacheList: list = []
            map: list = ["_db_table"]
            self.args["_db_table"] = self._c()
            map += self.map
            for i in map:
                cacheList.append(_cache)
                _cache = _cache.get(self.args.get(i))
                if _cache == None:
                    raise Exception("Key Not Found.")

            _cache[k] = v

            listLength = len(cacheList) - 1
            while listLength >= 0:
                _temp = cacheList[-listLength]
                _temp[map[-listLength]] = _cache
                _cache = _temp
                listLength -= 1

            Cache.cacheList = _cache
            '''

            self.cache[k] = v

            idx_str: str = f"['{self._c()}']"
            for i in self.map:
                ob = self.args.get(i)
                idx_str += f"[\"{ob}\"]"
            exec(f"Cache.cacheList{idx_str} = {eval(str(self.cache))}")
        return self

    def __insert(self):
        if not self.format_insert:
            return False

        col_name: str = ""
        flag: bool = False
        for i in self.col:
            name = i.get('name')
            if flag:
                col_name += ", "
            else:
                flag = True
            col_name += f"`{name}`"

        vs: str = ""
        vsl: list = []
        outer_flag: bool = False
        for i in self.format_insert:
            tmp_str: str = ""
            flag: bool = False
            for _ in i:
                if flag:
                    tmp_str += ", "
                else:
                    flag = True
                tmp_str += "?"
            if outer_flag:
                vs += ", "
            else:
                outer_flag = True

            vs += f"({tmp_str})"
            vsl += i

        print(self.sql_insert.format(self._getTableName(), col_name, vs), tuple(vsl))
        sql_driver.execute(self.sql_insert.format(self._getTableName(), col_name, vs), tuple(vsl))
        sql_driver.commit()

    def __update(self):
        if not self.format_update:
            return False

        tmp_str: str = ""
        v_list: list = []
        flag: bool = False
        for i in self.format_update:
            if flag:
                tmp_str += ", "
            else:
                flag = True
            k, v = i.get("key"), i.get("value")
            tmp_str += f"`{k}` = ?"
            v_list.append(v)
        sql = self.sql_update.format(self._getTableName(), tmp_str, self.sql_whereCase)
        sql_driver.execute(sql, tuple(v_list + self.sql_whereList))
        sql_driver.commit()

    def _refresh(self, insert_flag: bool = False, kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.cache = Cache.get(self._c())

        # 初始化数据表
        if self.cache is None:
            self._createTable()
            self.cache = Cache.get(self._c())

        # 获取具体cache
        c_iter = 0
        for i in self.map:
            _cache = self.cache
            self.cache = self.cache.get(str(self.args.get(i)))
            if self.cache is None:
                if insert_flag:
                    self._insert(**kwargs)
                    self.exists = False
                    self.cache = _cache.get(str(self.args.get(i)))
                else:
                    raise Exception("Key Not Found.")
            c_iter += 1


class ListModel(ModelBase):
    cache: list = []
    format_delete: list = []

    def _sync(self):
        self.__insert()
        self.__update()
        self.__delete()

    def __del__(self):
        self._sync()

    def __init__(self) -> None:
        # Init class vars.
        for i in dir(self):
            if i[0:1] == "_" or callable(getattr(self, i)):
                continue
            var_type = type(getattr(self, i))
            setattr(self, i, var_type(getattr(self, i)))

        # Init data.
        self._getCol()
        self._refresh()

    def _refresh(self):
        self.cache = Cache.get(self._c())

        if self.cache is None:
            self._createTable()

            # Load cache.
            sql = self.sql_select.format(self._getTableName())
            data = sql_driver.execute(sql)
            Cache.set(self._c(), data)

            self.cache = Cache.get(self._c())

        self.cache = list(self.cache)
        return self

    def _set(self, where: dict, **kwargs):
        for i in self.cache:
            flag = True
            for k, v in where.items():
                if i.get(k) != type(i.get(k))(v):
                    flag = False
                    break
            if flag is False:
                continue

            for k, v in kwargs.items():
                i[k] = v

            self.format_update.append({
                "whereCase": self._refreshWhereCase(**where),
                "update": kwargs
            })

            return self

    def _get(self, **where) -> list:
        return_list = list()
        for i in self.cache:
            flag = True
            for k, v in where.items():
                if i.get(k) != type(i.get(k))(v):
                    flag = False
                    break
            if flag is True:
                return_list.append(i)
        return return_list

    def _getAll(self) -> list:
        return self.cache

    def _delete(self, **where) -> dict:
        for i in self.cache:
            flag = True
            for k, v in where.items():
                if i.get(k) != type(i.get(k))(v):
                    flag = False
                    break
            if flag is True:
                self.format_delete.append(self._refreshWhereCase(**where))

                self.cache.remove(i)
                Cache.cacheList[self._c()].remove(i)
                return i
        return dict()

    def _refreshWhereCase(self, **where):
        # 生成where子句
        sql_whereCase: str = ""
        sql_whereList: list = []

        flag: bool = False
        for k, v in where.items():
            if flag:
                sql_whereCase += " AND "
            else:
                flag = True
            sql_whereCase += f"`{k}` = ?"
            sql_whereList.append(v)

        return sql_whereCase, sql_whereList

    def _insert(self, **kwargs):
        if kwargs:
            # 更新到同步列表
            insertList: list = []
            for i in self.col:
                v = kwargs.get(i.get('name'))
                if v is None:
                    _v = getattr(self, i.get('name'))()
                    if isinstance(_v, tuple) or isinstance(_v, list):
                        v = _v[1]
                insertList.append(v)
            self.format_insert.append(insertList)

        for i in self.col:
            i = i.get('name')
            if kwargs.get(i) is None:
                default = getattr(self, i)()
                if isinstance(default, list) or isinstance(default, tuple):
                    kwargs[i] = default[1]

        self.cache.append(kwargs)
        Cache.set(self._c(), self.cache)

        return self

    def _createTable(self):
        tmp_str: str = ""
        flag: bool = False
        tmp_list: list = self.col + self.format_createTable

        for i in tmp_list:
            if flag:
                tmp_str += ", "
            else:
                flag = True
            if isinstance(i, dict):
                tmp_str += i.get("default")
            elif isinstance(i, str):
                tmp_str += i
        sql = self.sql_createTable.format(self._getTableName(), tmp_str)
        sql_driver.execute(sql)
        sql_driver.commit()

    def __insert(self):
        col_name: str = ""
        flag: bool = False
        for item in self.col:
            name = item.get('name')
            if flag:
                col_name += ", "
            else:
                flag = True
            col_name += f"`{name}`"

        for i in self.format_insert:
            tmp_str: str = ""
            flag: bool = False
            for _ in i:
                if flag:
                    tmp_str += ", "
                else:
                    flag = True
                tmp_str += "?"

            vs: str = f"({tmp_str})"
            vsl: list = []
            for item in i:
                vsl.append(item)

            sql_driver.execute(self.sql_insert.format(self._getTableName(), col_name, vs), tuple(vsl))
            sql_driver.commit()

    def __update(self):
        for i in self.format_update:
            sql_whereCase = i.get("whereCase")[0]
            sql_whereList = i.get("whereCase")[1]
            update = i.get("update")

            tmp_str: str = ""
            vList: list = []
            flag: bool = False
            for k, v in update.items():
                if flag:
                    tmp_str += ", "
                else:
                    flag = True
                tmp_str += f"`{k}` = ?"
                vList.append(v)

            sql = self.sql_update.format(self._getTableName(), tmp_str, sql_whereCase)
            sql_driver.execute(sql, tuple(vList + sql_whereList))
            sql_driver.commit()

    def __delete(self):
        for i in self.format_delete:
            sql_driver.execute(self.sql_delete.format(self._getTableName(), i[0]), tuple(i[1]))
            sql_driver.commit()


# debug
class debugModel(DictModel):
    db_table = "test_test"
    map = ["uuid"]

    def uuid(self):
        return "varchar(255) NOT NULL"

    def name(self):
        return "varchar(255) NOT NULL"

    def age(self):
        return "int(11) NOT NULL"


if __name__ == '__main__':
    debug = debugModel(uuid="your-uuid", age=114, name="homo")
    print(debug._getAll())
    print(debug._get("age"))
    debug._set(name="test", age=810)
    print(debug._getAll())
    print(debug._get("name"))