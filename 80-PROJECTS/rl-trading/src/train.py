#!/usr/bin/env python3
"""
RL Training Loop Skeleton for rl-trading
PRM (Process Reinforcement Model) training with GRPO-style policy updates.
Minimal viable loop: env.step() -> policy inference -> policy.update().
"""
import argparse
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional


# ── Config ──────────────────────────────────────────────────────────────────
@dataclass
class TrainConfig:
    episodes: int = 100
    batch_size: int = 32
    horizon: int = 20          # max steps per episode
    lr: float = 1e-4
    gamma: float = 0.99         # discount factor
    ollama_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.5:0.8b"
    device: str = "cpu"
    save_dir: str = "./checkpoints"


# ── Environment Interface ───────────────────────────────────────────────────
@dataclass
class StepResult:
    observation: dict
    reward: float
    done: bool
    info: dict = field(default_factory=dict)


class MockEnv:
    """Minimal trading env for skeleton — replace with real trading env."""
    def __init__(self, episode_len: int = 20):
        self.episode_len = episode_len
        self.t = 0
        self.portfolio = 10000.0

    def reset(self) -> dict:
        self.t = 0
        self.portfolio = 10000.0
        return self._obs()

    def step(self, action: dict) -> StepResult:
        self.t += 1
        # Mock: random reward
        reward = (hash(str(action)) % 100 - 50) / 100.0
        self.portfolio *= (1 + reward * 0.01)
        done = self.t >= self.episode_len
        return StepResult(
            observation=self._obs(),
            reward=reward,
            done=done,
            info={"portfolio": self.portfolio, "step": self.t}
        )

    def _obs(self) -> dict:
        return {
            "portfolio": self.portfolio,
            "step": self.t,
            "balance": self.portfolio,
        }


# ── Policy (mock Ollama inference) ────────────────────────────────────────────
class Policy:
    """Policy that calls Ollama for action selection."""
    def __init__(self, config: TrainConfig):
        self.config = config
        self.theta = {}  # trainable params — initialized empty (from-scratch PRM)
        self._session_id = str(uuid.uuid4())[:8]

    def act(self, observation: dict, temperature: float = 0.6) -> dict:
        """
        Query Ollama for action.
        Returns dict with 'action' key (trade signal: buy/sell/hold + size).
        """
        import urllib.request
        import urllib.error

        prompt = self._build_prompt(observation)
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": temperature,
            "options": {"num_predict": 64},
            "session_id": self._session_id,
        }

        try:
            req = urllib.request.Request(
                f"{self.config.ollama_url}/api/generate",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            text = result.get("response", "").strip().lower()
            return self._parse_action(text)
        except Exception as e:
            # Fallback: random action on inference failure
            import random
            signals = ["buy", "sell", "hold"]
            sizes = [0.1, 0.25, 0.5, 1.0]
            return {"signal": random.choice(signals), "size": random.choice(sizes)}

    def _build_prompt(self, obs: dict) -> str:
        return (
            f"Portfolio: ${obs.get('portfolio', 0):.2f} | "
            f"Step: {obs.get('step', 0)} | "
            f"Briefly recommend: buy, sell, or hold with position size (0.1-1.0). "
            f"Respond with only: signal=<buy|sell|hold> size=<0.1|0.25|0.5|1.0>"
        )

    def _parse_action(self, text: str) -> dict:
        import re
        signal = "hold"
        size = 0.25
        sig_m = re.search(r"signal\s*=\s*(\w+)", text)
        sz_m = re.search(r"size\s*=\s*([\d.]+)", text)
        if sig_m: signal = sig_m.group(1).lower()
        if signal not in ("buy", "sell", "hold"): signal = "hold"
        if sz_m:
            try: size = min(1.0, max(0.1, float(sz_m.group(1))))
            except: pass
        return {"signal": signal, "size": size}

    def update(self, trajectory: list) -> dict:
        """
        PRM/GRPO-style policy update.
        trajectory: list of (obs, action, reward, next_obs) tuples.
        Returns training stats dict.
        """
        # ── Compute returns (discounted cumulative rewards) ──────────────────
        gamma = self.config.gamma
        returns = []
        G = 0
        for _, _, r, _ in reversed(trajectory):
            G = r + gamma * G
            returns.append(G)
        returns = list(reversed(returns))

        # Normalize advantages
        if len(returns) > 1:
            mean = sum(returns) / len(returns)
            std = (sum((r - mean) ** 2 for r in returns) / len(returns)) ** 0.5
            std = std if std > 1e-8 else 1.0
            advantages = [(r - mean) / std for r in returns]
        else:
            advantages = [0.0]

        # ── Mock gradient update (placeholder for real PRM training) ──────
        # In a full implementation, this would:
        # 1. Compute log_prob(action) from policy
        # 2. policy_loss = -E[advantage * log_prob]
        # 3. Backprop through neural network weights
        loss = sum(-adv * (i + 1) * 0.001 for i, adv in enumerate(advantages))
        grad_norm = abs(loss) * 0.01  # mock gradient norm

        return {
            "loss": float(loss),
            "grad_norm": float(grad_norm),
            "mean_return": float(sum(returns) / len(returns)) if returns else 0.0,
            "steps": len(trajectory),
        }


# ── Training Loop ─────────────────────────────────────────────────────────────
def train(config: TrainConfig):
    env = MockEnv(episode_len=config.horizon)
    policy = Policy(config)

    print(f"\n{'='*60}")
    print(f"RL Training — {config.episodes} episodes, batch={config.batch_size}")
    print(f"Model: {config.model} @ {config.ollama_url}")
    print(f"{'='*60}\n")

    all_stats = []
    for ep in range(1, config.episodes + 1):
        obs = env.reset()
        trajectory = []
        episode_reward = 0.0

        for _ in range(config.horizon):
            action = policy.act(obs)
            result = env.step(action)
            next_obs, reward, done = result.observation, result.reward, result.done
            trajectory.append((obs, action, reward, next_obs))
            episode_reward += reward
            obs = next_obs
            if done: break

        stats = policy.update(trajectory)
        stats["episode"] = ep
        stats["episode_reward"] = episode_reward
        all_stats.append(stats)

        if ep % max(1, config.episodes // 10) == 0 or ep == 1:
            mr = stats["mean_return"]
            er = episode_reward
            print(
                f"  Ep {ep:4d} | reward={er:+.3f} | "
                f"mean_return={mr:+.3f} | loss={stats['loss']:.4f} | "
                f"|∇|={stats['grad_norm']:.4f}"
            )

    # ── Summary ───────────────────────────────────────────────────────────
    avg_reward = sum(s["episode_reward"] for s in all_stats) / len(all_stats)
    print(f"\n✅ Training complete | avg_reward={avg_reward:+.3f}")
    return all_stats


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="RL Trading Training Loop")
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen3.5:0.8b")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    config = TrainConfig(
        episodes=args.episodes,
        batch_size=args.batch_size,
        horizon=args.horizon,
        lr=args.lr,
        gamma=args.gamma,
        ollama_url=args.ollama_url,
        model=args.model,
        device=args.device,
    )
    train(config)


if __name__ == "__main__":
    main()
