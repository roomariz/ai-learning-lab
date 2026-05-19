01 Messages-Only Memory
=======================
[config] Project root: D:\workspace\open-source\ai-learning-lab\projects\ollama-agent-state-middleware-lab
[config] .env path: D:\workspace\open-source\ai-learning-lab\projects\ollama-agent-state-middleware-lab\.env
[config] .env loaded: True
[config] MODEL_PROVIDER: ollama
[config] OLLAMA_MODEL: qwen2.5-coder:7b
[config] OLLAMA_BASE_URL: http://localhost:11434

Call 1: user shares a preference
================================

USER:
My preferred programming language is Python. Please remember that.

ASSISTANT:
Got it! You prefer Python for your programming tasks. How can I assist you with it today?

Call 2: fresh call without previous messages
============================================

USER:
What is my preferred programming language?

ASSISTANT:
I'm sorry, but I don't have access to your personal preferences or settings. How can I assist you with something else today?

Conclusion
==========
The second call does not include the first message. The model therefore has no reliable way to know the user's preference. This is the core limitation of isolated message calls: the model only sees the messages passed into the current invocation.