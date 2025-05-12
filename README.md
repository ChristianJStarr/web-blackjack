# Web Blackjack

![Web Blackjack](https://www.blackjackgame.site/static/blackjack-preview.png)

A modern, multiplayer online blackjack game where you can play with friends or other players from around the world. Built with Flask and Socket.IO for real-time gameplay.

## ♠️ Features

- **Live Multiplayer Games**: Join tables with other players in real-time
- **User Accounts**: Create accounts to track your progress and earnings
- **Guest Play**: Join quickly as a guest with no registration required
- **Realistic Gameplay**: Authentic blackjack rules and mechanics
- **Leaderboards**: Compete to be the top player
- **Responsive Design**: Play on desktop or mobile devices

## 🎮 Play Now

Visit [www.blackjackgame.site](https://www.blackjackgame.site) to start playing!

## 🚀 Getting Started (For Developers)

### Prerequisites

- Python 3.9 or higher
- MySQL database
- Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ChristianJStarr/web-blackjack.git
   cd web-blackjack
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=mysql+mysqlconnector://user:password@localhost/blackjack
   ```

5. Run the application:
   ```bash
   python run.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## 🏗️ Project Structure

```
web-blackjack/
├── blackjack/              # Main package
│   ├── __init__.py         # Application factory
│   ├── models/             # Database models
│   ├── game/               # Game logic
│   ├── api/                # API routes
│   ├── web/                # Web routes
│   ├── auth/               # Authentication
│   ├── templates/          # Templates
│   └── static/             # Static files
├── config.py               # Configuration
├── requirements.txt        # Dependencies
└── run.py                  # Application runner
```

## 🧪 Testing

Run the test suite with:

```bash
python -m pytest
```

## 📄 API Documentation

API documentation is available at `/api/v1/doc` when the application is running.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Card images from [OpenGameArt](https://opengameart.org)
- Sound effects from [FreeSound](https://freesound.org)
- Special thanks to the Flask and Socket.IO communities 