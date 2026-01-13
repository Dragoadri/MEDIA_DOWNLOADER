#!/bin/bash

# Script para subir el proyecto a GitHub
# ⚠️ IMPORTANTE: NO ejecutes el echo del README.md porque ya existe uno completo

echo "🚀 Inicializando repositorio Git..."
git init

echo "📦 Añadiendo todos los archivos..."
git add .

echo "💾 Creando commit inicial..."
git commit -m "Initial commit: YouTube Downloader Desktop App"

echo "🌿 Configurando rama main..."
git branch -M main

echo "🔗 Añadiendo repositorio remoto..."
git remote add origin https://github.com/Dragoadri/YOUTUBE_DOWNLOAD.git

echo "⬆️ Subiendo a GitHub..."
git push -u origin main

echo "✅ ¡Proyecto subido exitosamente a GitHub!"
