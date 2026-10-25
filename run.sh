#!/usr/bin/env bash
# Quick Start Script for Kivi-Vyaapaar

cd "$(dirname "$0")"
echo "=========================================================="
echo " Starting Kivi-Vyaapaar (Sarvam AI Hackathon @ IIT BHU) "
echo " Voice-First Sovereign AI Coworker for Bharat Merchants  "
echo "=========================================================="

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
