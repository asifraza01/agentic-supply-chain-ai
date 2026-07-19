#!/bin/bash
echo "🔄 Restarting Zookeeper to clear stale sessions..."
docker compose restart zookeeper
sleep 5
echo "🚀 Starting Kafka..."
docker compose up -d kafka
sleep 5
echo "✅ Verifying..."
docker compose ps