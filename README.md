## 1.pip -r requirements.txt \
## 2.new .env in root add the following  
#### DATABASE_URL=mysql+pymysql://user:password@localhost:3306/db_name #your_mysql_user_password_dbname 
#### SECRET_KEY=xxxxxxx #your_secret_key_for_password_hashing 
#### ALGORITHM=HS256
#### ACCESS_TOKEN_EXPIRE_MINUTES=300
## 3.run create_table.py 
## 4.run fetch_pubmed_data 
## 5.in root uvicorn main:app --reload 
## 6.on http://127.0.0.1:8000:docs query interface