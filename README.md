# Apartment Tracker Automation

A Python based automation system designed to eliminate manual data entry in apartment hunting. Built for professionals who value efficiency or identify as lazy (like myself).

## What it does

Takes raw apartment addresses and automatically enriches them with:
- Property names from Google Places
- Accurate commute times to your desired location (car, bike, transit)
- Direct Google Maps links
- City extraction and standardization

## Architecture

- **Flask API**: Handles webhook requests and orchestrates data processing
- **Google Maps integration**: Fetches property details and routing information
- **Google Sheets API**: Automated spreadsheet updates
- **n8n workflow**: Monitors sheet changes and triggers processing

## Built for scale

Designed with Railway deployment and production workflows in mind. Handles rate limiting, error recovery, and batch processing for comprehensive apartment research.

## Tech stack

Python, Flask, Google Maps API, Google Sheets API, Railway, n8n
