# Web Blackjack 🃏

Welcome to **Web Blackjack**, a multiplayer online Blackjack experience! Players can join unique game tables and compete in real-time against others, all through an intuitive web interface.

## Features ✨

- **Multiplayer Gameplay**: Join or create unique game tables using Socket.IO for real-time interaction.
- **Dynamic Game Rooms**: Access unique tables via URLs like `/game/2Qk5` where others can join and play together.
- **Web Interface**: Sleek and responsive design using HTML, JavaScript, and Less.
- **Dockerized Setup**: Easily deploy with Docker and Docker Compose.
- **Live Demo**: Check out the live version at [blackjackgame.site](https://blackjackgame.site).

## Getting Started 🚀

### Prerequisites

- Python 3.x
- Docker (optional for containerized deployment)

### Installation

1. **Clone the repo**:
   ```
   git clone https://github.com/ChristianJStarr/web-blackjack.git
   cd web-blackjack
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

#### Locally
```
python app.py
```
Visit `http://localhost:5```` and start a game by navigating to `/game/<your-table-id>`. Share the URL with friends to join the same table.

#### With Docker
```
docker-compose up --build
```
The application will be available at `http://localhost:5000`.

## How to Play 🕹️

1. Start a new game by visiting a unique URL like `/game/2Qk5`.
2. Share the URL with others so they can join your table.
3. Place your bets, hit, or stand in an attempt to win against the dealer and your friends!

## File Structure 🗂️

- **blackjack.py**: Core game logic.
- **bots.py**: AI bot strategies (optional).
- **app.py**: Flask application with Socket.IO integration.
- **templates/**: HTML templates.
- **static/**: Frontend assets (CSS, JavaScript, images).
- **DockerFile**: Configuration for Docker image.
- **docker-compose.yml**: Docker Compose setup.

## Contributing 🤝

Feel free to fork this repository and submit pull requests. Any contributions are welcome!

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.