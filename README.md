# blackjack-pygame
BlackJack game ♠️♥️♣️♦️

This is a Blackjack game implemented using Python and the Pygame library. The game provides a casino-like experience with a user-friendly interface, allowing players to play Blackjack, bet, manage virtual currency, purchase in-game credits, and change wallpapers. The payment system is designed to simulate a realistic transaction process without using real financial data.

![Image](https://github.com/user-attachments/assets/7c90f283-e72a-48be-ade7-a7b9845657c6)

About the project

I am Necsulea Florentina, a student at the Faculty of Automation, Computers, and Electronics in Craiova, Romania, studying Multimedia Systems Engineering. This Blackjack game was developed as a key project for the Algorithm Design course, guided by my professors. The course focuses on creating efficient algorithms, and this project showcases those skills through an interactive card game. 

Inspired by the idea of blending entertainment with technical precision, I built this game over several weeks, involving planning, coding, testing, and refinement. The objectives included implementing classic Blackjack rules, a virtual currency system, and customizable wallpapers. The Blackjack class in blackjack.py uses Pygame for the GUI, JSON for persistent storage, and includes a simulated payment system for purchasing in-game credits. Algorithms for card shuffling, hand evaluation, and game state management were optimized for efficiency.

Features

-Classic Blackjack Gameplay: Bet, hit, stand, and compete against the dealer with standard rules.

-Virtual Currency: Start with $1000 to bet or buy wallpapers; purchase additional credits via a simulated payment system.

-Customizable Wallpapers: Unlock and switch between "default," "wood," and "flower" backgrounds.

-Persistent Storage: Saves balance, wallpapers, and stats (games, wins, losses, pushes) in game_state.json.

-Responsive UI: Pygame-powered interface with buttons, text inputs.

-Keyboard Controls: Press Space to hit and Enter to stand during gameplay.

-Statistics Tracker: Displays games played, wins, losses, and pushes at game over.

-Win/Loss Outcomes: Clear results ("Player wins!", "Dealer wins!", "Push!") with dynamic scoring and balance updates.

Technologies Used

-Backend: Python, with core logic in blackjack.py.

-Frontend: Pygame for graphical interface development.

-Data Management: JSON for persistent storage of game state.

-Development Tools: Native Python libraries and a local development environment.

Known Issues and Limitations

-Asset Dependencies: The game requires specific image files (cards/, chip_*.png, wallpaper*.png) in the assets/ folder. Missing files cause crashes unless handled by error checks.

-Payment Simulation: The payment system is purely simulated and lacks real transaction processing, limiting its use to in-game currency purchases.

-Single-Player Only: No multiplayer or AI difficulty options, limiting gameplay variety.

-Keyboard Controls: While Space (hit) and Enter (stand) are supported, other keyboard shortcuts are not implemented, potentially reducing accessibility.

 Requirements
 
 Python Version 3.6 or higher.
 Pygame install via pip install pygame.

 ![image](https://github.com/user-attachments/assets/b8e3c5eb-9e37-4a3a-8941-57002839b6d9)
 
 ![image](https://github.com/user-attachments/assets/54a1a881-4912-4ff3-ac3e-c9cda0bcea58)

 ![image](https://github.com/user-attachments/assets/26adc6a0-4ae4-4198-909a-110c532a1858)

 ![image](https://github.com/user-attachments/assets/cc68b6ce-b675-434d-958b-3ca0c0467e50)

All the images used in the Blackjack game, such as the card images, chips, and backgrounds, are located in the 'assets' folder within the project directory. This folder is essential for the game to function properly, so please do not delete or move it. If you wish to customize the game's appearance, you can replace the images in this folder with your own, making sure to keep the same file names and formats.

Disclaimer: This project is the product of the Algorithm Design laboratory at the Faculty of Automation, Computers, and Electronics, University of Craiova (http://ace.ucv.ro/). It is intended for educational purposes and may include limitations or incomplete features. Use it at your own risk, and conduct thorough testing and configuration before considering any production deployment. 

Thank you for immersing yourself in my project! I hope you find Blackjack both captivating and instructive! I warmly welcome your feedback or suggestions to further enrich this academic endeavor.



