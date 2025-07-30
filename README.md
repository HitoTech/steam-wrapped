# 🎮 Steam Wrapped

A Python application that generates beautiful visual summaries of your Steam gaming activity, similar to Spotify Wrapped. Create stunning images showcasing your 3 most played games from the last two weeks.

![Steam Wrapped Example](steam_story.png)

## ✨ Features

- 📊 **Visual Game Summary**: Generate Instagram-story style images of your gaming activity
- 🎯 **Recent Activity Focus**: Highlights games played in the last 2 weeks
- 🎨 **Beautiful Design**: Professional-looking graphics with shadows, gradients, and Steam branding
- 🌍 **Localization Support**: Customizable date formatting and locale settings
- 🔒 **Secure Configuration**: Environment variables for API keys and sensitive data
- 📱 **Social Media Ready**: Output optimized for sharing (1080x1920 resolution)

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Steam account with public profile/game details
- Steam Web API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd steam-wrapped
   ```

2. **Install dependencies using PDM**:
   ```bash
   pip install pdm
   pdm install
   ```

   *Or with pip*:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```

   Edit `.env` with your Steam credentials:
   ```env
   STEAM_API_KEY=your_steam_api_key_here
   STEAM_USER_ID=your_steam_user_id_here
   LOCALE=fr_FR
   ```

4. **Run the application**:
   ```bash
   pdm run python main.py
   ```

## 🔧 Configuration

For detailed configuration instructions, see [ENV_SETUP.md](ENV_SETUP.md).

## 🎯 Usage

### Basic Usage

```bash
# Generate a Steam Wrapped image for the last 2 weeks
pdm run python main.py
```

The application will:
1. Fetch your recent gaming activity from Steam
2. Generate a beautiful summary image
3. Save it as `steam_story.png` in the project directory

## 🛠️ Development

### Code Quality Tools

This project uses several tools to maintain code quality:

```bash
# Format code with Black
pdm run black .

# Lint with Ruff
pdm run ruff check . --fix

# Run all quality checks
pdm run all
```

## 📦 Dependencies

### Core Dependencies
- **requests**: HTTP requests for Steam API
- **httpx**: Modern async HTTP client
- **python-dotenv**: Environment variable management
- **Pillow (PIL)**: Image generation and manipulation
- **rich**: Beautiful console output
- **babel**: Internationalization and date formatting

### Development Dependencies
- **black**: Code formatting
- **ruff**: Fast Python linter
- **isort**: Import sorting
- **pre-commit**: Git hooks for code quality

## 🐛 Troubleshooting

### Common Issues

**"Missing STEAM_API_KEY or STEAM_USER_ID"**
- Check that your `.env` file exists and contains valid credentials
- Verify your Steam profile is set to public

**"HTTP 403 Forbidden"**
- Your Steam profile game details might be private
- Check your Steam privacy settings

**"No games found"**
- You might not have played any games in the last 2 weeks
- Verify your Steam ID is correct

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct before submitting pull requests.

---

**Note**: This is an unofficial project and is not affiliated with Valve Corporation or Steam.