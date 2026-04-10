---
id: 221208073-constitutional-ai-harmlessness-from-ai-feedback
title: [2212.08073] Constitutional AI: Harmlessness from AI Feedback
category: AI
tags: [论文解读, 2212.08073]
arxiv: 2212.08073
created: 2026-04-10T13:08:24.020Z
---

# [2212.08073] Constitutional AI: Harmlessness from AI Feedback

**arXiv**: 2212.08073 | **Author**: 

## 摘要

As AI systems become more capable, we would like to enlist their help to supervise other AIs. We experiment with methods for training a harmless AI assistant through self-improvement, without any human labels identifying harmful outputs. The only human oversight is provided through a list of rules or principles, and so we refer to the method as &#39;Constitutional AI&#39;. The process involves both a supervised learning and a reinforcement learning phase. In the supervised phase we sample from an initial model, then generate self-critiques and revisions, and then finetune the original model on revised responses. In the RL phase, we sample from the finetuned model, use a model to evaluate which of the two samples is better, and then train a preference model from this dataset of AI preferences. We then train with RL using the preference model as the reward signal, i.e. we use &#39;RL from AI Feedback&#39; (RLAIF). As a result we are able to train a harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections to them. Both the SL and RL methods can leverage chain-of-thought style reasoning to improve the human-judged performance and transparency of AI decision making. These methods make it possible to control AI behavior more precisely and with far fewer human labels.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）
