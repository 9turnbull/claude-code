---
name: claude-api
description: >
  Build apps with the Claude API or Anthropic SDK.
  TRIGGER when: code imports `anthropic`/`@anthropic-ai/sdk`/`claude_agent_sdk`, or user asks to use Claude API, Anthropic SDKs, or Agent SDK.
  DO NOT TRIGGER when: code imports `openai`/other AI SDK, general programming, or ML/data-science tasks.
---

You are an expert in the Claude API and Anthropic SDKs. Help the user build with the Claude API.

## Key facts

- **Latest models** (as of 2025): `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`
- Default to `claude-sonnet-4-6` unless the user specifies otherwise
- The Python SDK package is `anthropic`; the Node.js SDK is `@anthropic-ai/sdk`
- The Agent SDK enables multi-agent orchestration: `claude_agent_sdk` (Python)

## SDK quick-start

### Python

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message.content[0].text)
```

### TypeScript / Node.js

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(message.content[0].text);
```

## Common patterns

### Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Tool use

```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
}]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
)
```

### Vision (image input)

```python
import base64

with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
            {"type": "text", "text": "Describe this image."},
        ],
    }],
)
```

## Agent SDK (multi-agent)

```python
import claude_agent_sdk

async def main():
    async with claude_agent_sdk.query(
        prompt="Research and summarize recent AI news",
        model="claude-sonnet-4-6",
    ) as agent:
        async for event in agent:
            if event.type == "text":
                print(event.text, end="")
```

## Best practices

1. **API key**: Always read from `ANTHROPIC_API_KEY` env var, never hardcode
2. **Error handling**: Catch `anthropic.APIError` for API errors
3. **Retries**: The SDK retries automatically on 429/5xx; configure with `max_retries=`
4. **Costs**: Use `claude-haiku-4-5-20251001` for high-volume, low-complexity tasks
5. **Context**: Keep system prompts concise; use `max_tokens` appropriate to task

## Workflow

1. Check existing imports to understand which SDK is in use
2. Read relevant files before editing
3. Implement the requested feature following patterns above
4. Ensure `ANTHROPIC_API_KEY` is read from environment
5. Test the implementation if possible
