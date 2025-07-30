# Environment Variables Configuration

## Initial Setup

1. **Copy the configuration template**:
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file** with your real keys:
   ```bash
   # Steam API Configuration
   STEAM_API_KEY=ABC123DEF456GHI789  # Your real Steam API key
   STEAM_USER_ID=76561198000000000   # Your Steam ID

   # Optional configuration (keep default values if you want)
   LOCALE=fr_FR
   ```

## Getting your Steam keys

### Steam API Key
1. Go to https://steamcommunity.com/dev/apikey
2. Create an API key with your domain (or `localhost` for development)
3. Copy the key into your `.env` file

### Steam User ID
1. Go to your Steam profile
2. Use a site like https://steamid.io/ to convert your profile URL to Steam ID
3. Copy the 17-digit ID into your `.env` file

## Available variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `STEAM_API_KEY` | Steam API key | ✅ | - |
| `STEAM_USER_ID` | Steam user ID | ✅ | - |
| `LOCALE` | Language for dates | ❌ | `fr_FR` |