import re
from typing import List

from sqlalchemy.sql import text
from pydantic import BaseModel


class DataTableItem(BaseModel):
    draw: int
    length: int
    start: int
    columns: List[dict]
    order: List[dict]
    search: dict


class DataTable2:
    def __init__(self, db, item, search_fields=None, query=None, join_query=None, where_query='1=1'):
        self.item = item

        self.offset = item.start
        self.limit = item.length
        self.draw = item.draw
        self.search_keyword = item.search['value']
        self.search_fields = search_fields or []

        self.db = db

        self.query = query
        self.join_query = join_query
        self.where_query = where_query

    def get_search_query(self):
        global_queries = []
        for field in self.search_fields:
            if self.search_fields and self.search_keyword:
                global_queries.append('{} LIKE "{}%"'.format(field, self.search_keyword))

        select_queries = []
        for column in self.item.columns:
            data = column['data']
            search_value = column['search']['value']

            if not data:
                continue

            if data and search_value:
                split_data = data.split('__')
                time_data = search_value.split('~')
                if len(split_data) > 1:
                    if len(time_data) == 2:
                        select_queries.append('{} BETWEEN "{}" AND "{}"'.format('.'.join(split_data), time_data[0], time_data[1]))
                    else:
                        select_queries.append('{} LIKE "{}%"'.format('.'.join(split_data), search_value))

        global_query = ' OR '.join(global_queries) or '1=1'
        select_query = ' AND '.join(select_queries) or '1=1'

        query = '{} AND {} AND {}'.format(global_query, select_query, self.where_query)
        return query

    def select_query(self):
        if self.join_query:
            select_query = '{} {}'.format(self.query, self.join_query)
        else:
            select_query = self.query
        return select_query

    def get_query(self):
        search_query = self.get_search_query()
        order_by_query = self.get_order_by_query()
        select_query = self.select_query()
        query = '{} WHERE {} ORDER BY {} LIMIT {} OFFSET {}'.format(select_query, search_query, order_by_query,
                                                                    self.limit, self.offset)
        return query

    def get_order_by_query(self):
        field_number = self.item.order[0]['column']
        field_name = self.item.columns[field_number]['data']
        sort = self.item.order[0]['dir'].upper()
        return '{} {}'.format(field_name, sort)

    async def get_cnt(self):
        search_query = self.get_search_query()
        select_query = self.select_query()
        query = '{} WHERE {}'.format(select_query, search_query)
        cnt_query = re.sub(r'SELECT[\s\S]*FROM', 'SELECT COUNT(*) AS cnt FROM', query)

        row = await self.db.fetch_one(text(cnt_query))
        return dict(row)['cnt'] if row else 0

    async def get_cnt_all(self):
        query = self.select_query()
        cnt_query = re.sub(r'SELECT[\s\S]*FROM', 'SELECT COUNT(*) AS cnt FROM', query)

        row = await self.db.fetch_one(text(cnt_query))
        return dict(row)['cnt'] if row else 0

    async def search(self):
        query = self.get_query()
        rows = await self.db.fetch_all(text(query))
        rows = [dict(row) for row in rows]
        return dict(data=rows, recordsFiltered=await self.get_cnt(), recordsTotal=await self.get_cnt_all(), draw=self.draw)
