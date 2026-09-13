import express from 'express';
import fs from 'node:fs';
import path from 'node:path';

const app = express();

const PORT = Number(process.env.FLY_HEAVEN_BRIDGE_PORT || 8787);
const LOG_PATH = process.env.FLY_HEAVEN_LOG || '/tmp/fly_heaven.log';

const clients = new Set();

app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    log: LOG_PATH,
    clients: clients.size,
  });
});

app.get('/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
  });

  res.write('retry: 1000\n\n');
  clients.add(res);

  req.on('close', () => {
    clients.delete(res);
  });
});

function emit(type, payload = {}) {
  const body =
    `event: ${type}\n` +
    `data: ${JSON.stringify(payload)}\n\n`;

  for (const client of clients) {
    client.write(body);
  }
}

let offset = 0;
let carry = '';

// Start at EOF so old sessions are not replayed into the 3D fly.
try {
  offset = fs.statSync(LOG_PATH).size;
} catch {
  offset = 0;
}

function parseLine(line) {
  const smoke = line.match(
    /SMOKE #(\d+).*?song\s+([0-9.]+)s.*?loop\s+(\d+)\s+\|\s+(TRAINING|FROZEN)/
  );

  if (smoke) {
    emit('smoke', {
      count: Number(smoke[1]),
      songSeconds: Number(smoke[2]),
      loop: Number(smoke[3]),
      phase: smoke[4],
    });
    return;
  }

  if (line.includes('PAM07 reward')) {
    emit('reward', { active: true });
    return;
  }

  if (line.includes('TRAINING COMPLETE')) {
    emit('training_complete', {});
  }
}

function pollLog() {
  fs.stat(LOG_PATH, (statErr, stats) => {
    if (statErr) return;

    // run_heaven launch truncates the file before writing a new session.
    if (stats.size < offset) {
      offset = 0;
      carry = '';
    }

    if (stats.size === offset) return;

    const length = stats.size - offset;
    const stream = fs.createReadStream(LOG_PATH, {
      start: offset,
      end: stats.size - 1,
      encoding: 'utf8',
    });

    let chunk = '';

    stream.on('data', (data) => {
      chunk += data;
    });

    stream.on('end', () => {
      offset = stats.size;

      const text = carry + chunk;
      const lines = text.split(/\r?\n/);
      carry = lines.pop() || '';

      for (const line of lines) {
        parseLine(line);
      }
    });
  });
}

setInterval(pollLog, 100);

app.listen(PORT, '127.0.0.1', () => {
  console.log('FLY HEAVEN 3D bridge online');
  console.log(`SSE: http://127.0.0.1:${PORT}/events`);
  console.log(`Watching: ${LOG_PATH}`);
  console.log('Waiting for new MN9-driven SMOKE events...');
});
