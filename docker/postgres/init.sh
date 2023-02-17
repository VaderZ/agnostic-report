#!/bin/bash
# Error has to be ignored in case database already exists
psql -c "create database $DB_NAME" || true
