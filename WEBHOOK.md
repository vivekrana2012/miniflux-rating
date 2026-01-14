# Miniflux Webhook Server

Real-time event processing for Miniflux using webhooks instead of batch processing.

## Quick Start

1. **Complete main application setup first** (see main [README.md](README.md))

2. **Set webhook-specific environment variable:**
```bash
# Required: Webhook secret from Miniflux (Settings > Integrations > Webhook)
export MINIFLUX_WEBHOOK_SECRET="your-secret-here"

# Optional: Custom port (default: 9090)
export WEBHOOK_PORT="9090"
```

3. **Install FastAPI dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the webhook server:**
```bash
python webhook_server.py
```

The server will start on `http://0.0.0.0:9090` (or your custom port).

## Endpoints

### POST /webhook
Main webhook endpoint that receives Miniflux events and adds them to processing queue.

**Headers:**
- `X-Miniflux-Signature`: HMAC-SHA256 signature of the request body
- `X-Miniflux-Event-Type`: Event type (only `new_entries` is processed)

**Response:**
```json
{
  "status": "success",
  "queued": 2,
  "queue_size": 5
}
```

**Note:** Entries are added to an in-memory FIFO queue and processed asynchronously by a background thread.

### GET /health
Health check endpoint with queue status.

**Response:**
```json
{
  "status": "healthy",
  "queue_size": 3
}
```

## Configuring Miniflux

1. Go to **Settings > Integrations > Webhook**
2. Set **Webhook URL** to: `http://your-server:9090/webhook`
3. Set **Webhook Secret** to a secure random string (same as `MINIFLUX_WEBHOOK_SECRET`)
4. Enable the webhook
5. Save settings

## Security

- HMAC-SHA256 signature validation using constant-time comparison
- Only processes `new_entries` events
- Returns 401 for invalid signatures
- Logs all authentication failures

## How It Works

**Queue-Based Architecture:**

1. **Webhook receives entries** (immediate response):
   - Miniflux sends a webhook POST request to `/webhook` endpoint
   - Server validates the HMAC-SHA256 signature
   - Entries are added to an in-memory FIFO queue
   - Returns immediately with queue statistics

2. **Background processor** (polls every 60 seconds):
   - A daemon thread polls the queue every minute
   - Processes ONE entry at a time from the queue
   - Evaluates the blog post using Gemini API with `gemma-3-12b-it` model
   - Saves evaluation to `resources/{blog_id}.txt`
   - Stores rating in PostgreSQL database
   - Marks low/mid quality entries as read in Miniflux

**Model Selection:**
- Webhook queue: Uses `gemma-3-12b-it` (larger, better quality)
- Batch processing (`miniflux.py`): Uses `gemma-3-4b-it` (default, faster)

**Advantages over batch processing:**
- Event-driven (no polling Miniflux needed)
- Rate-limited processing (one entry per minute prevents API throttling)
- Non-blocking webhook responses
- Decoupled ingestion and processing

## Running in Production

### Using systemd

Create `/etc/systemd/system/miniflux-webhook.service`:

```ini
[Unit]
Description=Miniflux Rating Webhook Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project-miniflux-rating
EnvironmentFile=/path/to/.env
Environment="MINIFLUX_WEBHOOK_SECRET=your-webhook-secret"
ExecStart=/usr/bin/python3 /path/to/project-miniflux-rating/webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Note:** Use `EnvironmentFile` to load main application environment variables, and set webhook-specific `MINIFLUX_WEBHOOK_SECRET` separately.

Enable and start:
```bash
sudo systemctl enable miniflux-webhook
sudo systemctl start miniflux-webhook
sudo systemctl status miniflux-webhook
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9090

CMD ["python", "webhook_server.py"]
```

Build and run:
```bash
docker build -t miniflux-webhook .
docker run -p 9090:9090 \
  --env-file .env \
  -e MINIFLUX_WEBHOOK_SECRET=your-webhook-secret \
  miniflux-webhook
```

**Note:** Use `--env-file` to load main application environment variables, and set `MINIFLUX_WEBHOOK_SECRET` separately.

## Monitoring

Check logs for webhook activity:
```bash
# If running with systemd
journalctl -u miniflux-webhook -f

# If running directly (logs to logs/miniflux_rating.log)
tail -f logs/miniflux_rating.log
```

**Check queue status:**
```bash
curl http://your-server:9090/health
```

Look for these log entries:
- `"Queued entry {id}"` - Entry added to queue
- `"Processing queued entry {id}"` - Background processor started working
- `"Queue size: {n}"` - Current queue depth

## Troubleshooting

**Invalid signature errors:**
- Verify `MINIFLUX_WEBHOOK_SECRET` matches the secret in Miniflux Settings > Integrations > Webhook
- Check that the secret is set correctly in environment variables
- Ensure no extra whitespace in the secret value

**Webhook not triggering:**
- Verify Miniflux can reach your webhook URL (check network/firewall)
- Check if webhook is enabled in Miniflux settings
- Test with the `/health` endpoint first: `curl http://your-server:9090/health`

**Connection errors:**
- Ensure the webhook URL is accessible from Miniflux server
- Check firewall rules if running on different machines
- Verify port is not already in use: `lsof -i :9090`

**Processing errors:**
- Check logs for detailed error messages
- Verify all main application environment variables are set (see main README.md)
- Test the main application works first: `python miniflux.py` with max_entries=1

**Queue not processing:**
- Check `/health` endpoint to see current queue size
- Verify background thread is running (check logs for "Queue processor started")
- Processing happens every 60 seconds - wait at least one minute after queuing
- Check for errors in queue processor (logged as "Error processing queued entry")
