#!/bin/bash
# MattGPT React Repository Setup Script
# Run this on your local machine to recreate the repository

set -e

echo "🚀 Setting up MattGPT React repository..."

# Clone the empty repo
echo "📦 Cloning repository..."
git clone https://github.com/mcpugmire1/mattgpt-react.git
cd mattgpt-react

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p frontend/src/{components,services}
mkdir -p backend/{lambdas,prompts}
mkdir -p infrastructure/{lib,bin}
mkdir -p data

echo "✅ Repository structure created!"
echo ""
echo "📝 Next steps:"
echo "1. Download the full code archive from Claude Code environment"
echo "2. Extract it into this directory"
echo "3. Run: git push -u origin main"
echo ""
echo "Or use the file-by-file creation script (coming next)..."
