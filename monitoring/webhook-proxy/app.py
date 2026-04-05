#!/usr/bin/env python3

from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _sanitize_for_log(value):
    if value is None:
        return "None"
    return str(value).replace("\r", "").replace("\n", "")

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        logger.info(f"Received webhook: {_sanitize_for_log(data)}")
        
        if not DISCORD_WEBHOOK_URL:
            logger.error("DISCORD_WEBHOOK_URL not configured")
            return jsonify({"error": "Discord webhook not configured"}), 500
        
        alerts = data.get('alerts', [])
        
        for alert in alerts:
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            status = alert.get('status', 'unknown')
            
            if status == 'firing':
                if labels.get('severity') == 'critical':
                    color = 15158332  # Red
                else:
                    color = 16776960  # Yellow
            else:
                color = 3066993  # Green (resolved)
            
            discord_message = {
                "content": f"🚨 **Alert {status.upper()}**",
                "embeds": [{
                    "title": f"{labels.get('alertname', 'Unknown Alert')}",
                    "description": annotations.get('description', 'No description available'),
                    "color": color,
                    "fields": [
                        {
                            "name": "Severity",
                            "value": labels.get('severity', 'unknown').upper(),
                            "inline": True
                        },
                        {
                            "name": "Instance",
                            "value": labels.get('instance', 'unknown'),
                            "inline": True
                        },
                        {
                            "name": "Status",
                            "value": status.upper(),
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": f"Job: {labels.get('job', 'unknown')}"
                    }
                }]
            }
            
            # Send to Discord
            response = requests.post(DISCORD_WEBHOOK_URL, json=discord_message)
            
            if response.status_code == 204:
                logger.info(f"Successfully sent alert to Discord: {_sanitize_for_log(labels.get('alertname'))}")
            else:
                logger.error(f"Failed to send to Discord: {response.status_code} - {response.text}")
        
        return jsonify({"status": "success", "alerts_processed": len(alerts)}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
