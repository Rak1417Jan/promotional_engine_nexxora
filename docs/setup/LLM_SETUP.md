# LLM Setup Guide
## Using Groq (Free) or OpenAI

**Last Updated:** January 2025

---

## Overview

The platform supports two LLM providers:
1. **Groq** (Recommended - Free, Fast) - Open-source models like Llama 3.1, Mixtral
2. **OpenAI** (Paid) - GPT-4, GPT-3.5

**Default:** Groq (free and fast!)

---

## Option 1: Groq (Recommended - FREE) 🆓

### Why Groq?
- ✅ **100% Free** (with generous rate limits)
- ✅ **Extremely Fast** (up to 10x faster than OpenAI)
- ✅ **Open Source Models** (Llama 3.1, Mixtral)
- ✅ **No Credit Card Required**
- ✅ **Same API as OpenAI** (easy to switch)

### Setup Steps

1. **Get Free API Key:**
   - Go to [Groq Console](https://console.groq.com/)
   - Sign up (free, no credit card)
   - Navigate to **API Keys**
   - Click **"Create API Key"**
   - Copy the key (starts with `gsk_`)

2. **Add to .env:**
   ```bash
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your-api-key-here
   GROQ_MODEL=llama-3.1-70b-versatile
   ```

3. **Available Models:**
   - `llama-3.1-70b-versatile` - Best quality (recommended)
   - `llama-3.1-8b-instant` - Fastest, good for simple tasks
   - `mixtral-8x7b-32768` - Good balance

4. **Install Package:**
   ```bash
   pip install groq
   ```

### Groq Rate Limits (Free Tier)
- **30 requests/minute**
- **14,400 requests/day**
- More than enough for development and testing!

---

## Option 2: OpenAI (Paid)

### Setup Steps

1. **Get API Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up and add payment method
   - Get API key from **API Keys** section

2. **Add to .env:**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

3. **Install Package:**
   ```bash
   pip install openai
   ```

---

## Configuration

### Environment Variables

```bash
# LLM Provider Selection
LLM_PROVIDER=groq  # or "openai"

# Groq Configuration (if using Groq)
GROQ_API_KEY=gsk_your-key-here
GROQ_MODEL=llama-3.1-70b-versatile

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Model Comparison

| Model | Provider | Speed | Quality | Cost |
|-------|----------|-------|---------|------|
| llama-3.1-70b-versatile | Groq | ⚡⚡⚡ | ⭐⭐⭐⭐ | FREE |
| llama-3.1-8b-instant | Groq | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | FREE |
| mixtral-8x7b-32768 | Groq | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | FREE |
| gpt-4-turbo | OpenAI | ⚡⚡ | ⭐⭐⭐⭐⭐ | Paid |
| gpt-3.5-turbo | OpenAI | ⚡⚡⚡ | ⭐⭐⭐⭐ | Paid |

---

## Switching Providers

You can switch between providers anytime by changing `LLM_PROVIDER` in `.env`:

```bash
# Use Groq (Free)
LLM_PROVIDER=groq

# Use OpenAI (Paid)
LLM_PROVIDER=openai
```

No code changes needed! The service automatically uses the configured provider.

---

## Testing

### Test LLM Service

```python
from app.ml.llm_service import LLMService

llm = LLMService()

# Test text generation
response = llm.generate_text(
    prompt="Write a short welcome message for a gaming platform",
    system_prompt="You are a marketing copywriter"
)
print(response)
```

### Test via API

```bash
# Create AI campaign (uses configured LLM)
curl -X POST "http://localhost:8000/api/v1/campaigns/ai-generate?operator_id=1&objective=Welcome new players" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting

### Issue: "Groq API key not configured"
- Get free API key from https://console.groq.com
- Add `GROQ_API_KEY` to `.env`

### Issue: "Groq package not installed"
```bash
pip install groq
```

### Issue: Rate limit exceeded (Groq)
- Free tier: 30 requests/minute
- Wait a minute or upgrade to paid tier

### Issue: Want to use OpenAI instead
- Set `LLM_PROVIDER=openai` in `.env`
- Add `OPENAI_API_KEY` to `.env`

---

## Cost Comparison

### Groq (Free Tier)
- **Cost:** $0
- **Rate Limits:** 30 req/min, 14,400 req/day
- **Perfect for:** Development, testing, small to medium production

### OpenAI
- **Cost:** ~$0.01-0.03 per 1K tokens
- **Rate Limits:** Based on tier
- **Perfect for:** High-volume production, when you need GPT-4 quality

---

## Recommendation

**For Development & Testing:** Use Groq (Free, Fast)  
**For Production:** Start with Groq, upgrade to OpenAI if needed

---

## Next Steps

1. Get Groq API key: https://console.groq.com
2. Add to `.env` file
3. Restart server
4. Test AI features!

---

**Status:** ✅ Ready to use Groq (Free LLM)!
