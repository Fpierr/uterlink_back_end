#!/usr/bin/python3

from dotenv import load_dotenv
import os
import mysql.connector
import logging

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    DEVELOPER_EMAIL = os.getenv('DEVELOPER_EMAIL')
    SECRET_KEY = os.getenv('SECRET_KEY')

try:
    db = mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4'
    )
    logging.info("Successfully connected to the database")
except mysql.connector.Error as err:
    logging.error(f"Error connecting to the database: {err}")
    db = None
