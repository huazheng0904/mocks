# Mock Agentic Coding Exercise

This is a small practice repo for the Writer live agentic coding interview.

It simulates an AI chat agent that receives model tool calls, executes Python tools, sends tool results back, and returns a final answer. It does not require an OpenAI API key.

## Run

```bash
python -m unittest -v
```

## Your Task

The starting implementation in `agent.py` is intentionally incomplete.

Fix it so all tests pass:

- Parse tool-call arguments from JSON.
- Execute the requested tool.
- Preserve the tool call ID in the returned tool message.
- Send tool outputs back to the fake model.
- Continue the loop until the model returns final text.
- Handle multiple tool calls.
- Return useful error payloads for unknown tools or bad JSON.

Then add one new tool of your own and a test for it.

## Interview Practice Script

As you work, narrate:

- What you are inspecting.
- What invariant the agent loop should maintain.
- Which failure you reproduced.
- Why your patch is narrow.
- How you verified it.
