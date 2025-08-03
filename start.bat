:: Start PostgreSQL.
@echo off
cd "C:\Program Files\PostgreSQL\17\bin"
pg_ctl start -D "C:\Program Files\PostgreSQL\17\data"
:: cmd.exe //c start.bat to run in git bash.