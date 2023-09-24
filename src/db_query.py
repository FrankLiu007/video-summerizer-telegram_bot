## general database query functions

async  def select_data_from_database(conn, table0, **kwargs):
 
    query="SELECT * FROM "+ table0  ## table is a keyword in python, so use table as a variable name is not a good idea
    conditions=[]
    values = []
    for field, value in kwargs.items():
        conditions.append(f"{field} = ?")
        values.append(f"{value}")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    curr=await conn.execute(query, values)
    result=await curr.fetchall()
    await curr.close()
    return  result

async def delete_data_from_database(conn, table0, **kwargs):

    query="DELETE  FROM "+ table0  ## table is a keyword in python, so use table0 as a variable name is not a good idea
    conditions=[]
    values = []

    for field, value in kwargs.items():
        conditions.append(f"{field} = ?")
        values.append(f"{value}")
        
    query += " WHERE " + " AND ".join(conditions)
    curr=await conn.execute(query, values)
    await conn.commit()

    return 

async def insert_data_to_database(conn, table0, **kwargs):
        
    fields = ', '.join(kwargs.keys())
    placeholders = ', '.join(['?'] * len(kwargs))
    query = f"INSERT INTO {table0} ({fields}) VALUES ({placeholders})"  
    values = list(kwargs.values())

    #curr.execute(query, values)
    #conn.commit()
    async with conn.execute(query, values) as cursor:
        await conn.commit()
        return cursor.lastrowid

# update data in database is a little complex
async def update_data_to_database(conn, table0,  columns, conditions):

    """
    更新数据库记录。    
    :param conn: 数据库连接。
    :param columns: 字典格式的需要更新的列。
    :param conditions: 字典格式的table的条件。
    """        

      # 构建 SQL 更新语句
    update_query = f"UPDATE {table0} SET "

    update_query += ", ".join([f"{column} = ?" for column in columns])


    cc= ' AND '.join([f"{key} = ?" for key in conditions])

    update_query+= " WHERE " + cc

    values = list(columns.values()) + list(conditions.values())

    await conn.execute(update_query, values)
    await conn.commit()
    return 
