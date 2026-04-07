"""
RL Training Reporter — WebSocket-based metrics broadcaster.
Injects into slime training loop to push reward/loss/episodes to openclaw-dashboard.

Usage:
    from slime.utils.rl_reporter import RLTrainingReporter
    reporter = RLTrainingReporter(port=3848)
    reporter.start()

    # In train loop after async_train completes:
    reporter.report(rollout_id=rollout_id, reward=avg_reward, loss=loss_value, episodes=ep_count)
"""

import json
import socket
import threading
import time
import uuid
from collections import deque
from datetime import datetime


class RLTrainingReporter:
    """Minimal WebSocket reporter for RL training metrics."""

    def __init__(self, host="localhost", port=3848, max_history=500):
        self.host = host
        self.port = port
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
        self._clients = set()
        self._running = False
        self._server_thread = None
        self._lock = threading.Lock()

    def start(self):
        if self._running:
            return
        self._running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()

    def stop(self):
        self._running = False

    def report(self, rollout_id, reward=None, loss=None, episodes=None,
               learning_rate=None, policy_loss=None, value_loss=None, entropy=None, **extra):
        """Broadcast a training step metrics snapshot to all connected clients."""
        ts = datetime.utcnow().isoformat() + "Z"
        entry = {
            "rollout_id": rollout_id,
            "timestamp": ts,
            "reward": reward,
            "loss": loss,
            "episodes": episodes,
            "learning_rate": learning_rate,
            "policy_loss": policy_loss,
            "value_loss": value_loss,
            "entropy": entropy,
        }
        entry.update(extra)
        entry = {k: v for k, v in entry.items() if v is not None}

        with self._lock:
            self.history.append(entry)
            msg = f"data: {json.dumps(entry)}\n\n"
            dead = set()
            for client in self._clients:
                try:
                    client.sendall(msg.encode())
                except Exception:
                    dead.add(client)
            for client in dead:
                self._clients.discard(client)

    def get_history(self):
        with self._lock:
            return list(self.history)

    def _run_server(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(16)
        srv.settimeout(1.0)
        while self._running:
            try:
                client, addr = srv.accept()
            except socket.timeout:
                continue
            except Exception:
                break
            threading.Thread(target=self._serve_client, args=(client,), daemon=True).start()

    def _serve_client(self, client):
        try:
            # SSE handshake
            req = b""
            while b"\r\n\r\n" not in req:
                req += client.recv(4096)
            headers = req.decode("utf-8", errors="ignore")
            if "Upgrade: websocket" in headers:
                # Drop - no WS, only SSE
                client.close()
                return
            # SSE client — send current history then live updates
            client.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-cache\r\nConnection: keep-alive\r\nAccess-Control-Allow-Origin: *\r\n\r\n")
            with self._lock:
                for entry in self.history:
                    msg = f"data: {json.dumps(entry)}\n\n"
                    client.sendall(msg.encode())
            with self._lock:
                self._clients.add(client)
            # Keep-alive loop
            while self._running:
                try:
                    data = client.recv(1, socket.MSG_PEEK)
                    if not data:
                        break
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception:
            pass
        finally:
            with self._lock:
                self._clients.discard(client)
            try:
                client.close()
            except Exception:
                pass


# Global singleton
_reporter = None
_reporter_lock = threading.Lock()


def get_reporter(host="localhost", port=3848):
    global _reporter
    with _reporter_lock:
        if _reporter is None:
            _reporter = RLTrainingReporter(host=host, port=port)
            _reporter.start()
        return _reporter
