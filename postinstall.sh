#!/bin/bash
echo "Forcing reinstallation of key packages..."
pip install --no-cache-dir --force-reinstall huggingface-hub==0.13.4 sentence-transformers==2.2.0