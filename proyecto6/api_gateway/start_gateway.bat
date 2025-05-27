@echo off
cd %~dp0
uvicorn main:app --reload --port 8080
