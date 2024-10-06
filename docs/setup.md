# Pygame Setup on Raspberry Pi

This guide walks through setting up **Pygame** on a Raspberry Pi using Python 3.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS.
- Python 3 (installed by default on Raspberry Pi).
- Internet access.

---

## Step 1: System Update

Before installing Pygame, update your system:

1. Open a terminal and run the following commands:

    ```bash
    sudo apt update
    sudo apt upgrade
    ```

---

## Step 2: Install Python 3, pip, and Pygame

### 2.1 Install Python 3 and pip

Ensure `pip` (Python’s package manager) is installed for Python 3:

```bash
sudo apt install python3-pip
```

### 2.2 Create a Virtual Environment (Optional)

It’s a good practice to use a virtual environment for Python projects:

1. Create a virtual environment:

    ```bash
    python3 -m venv pygame_env
    ```

2. Activate the virtual environment:

    ```bash
    source pygame_env/bin/activate
    ```

### 2.3 Install Pygame

Once inside the virtual environment (or globally), install Pygame:

```bash
pip install pygame
```

---

## Step 3: Verify Pygame Installation

1. Create a test Python file:

    ```bash
    nano pygame_test.py
    ```

2. Add the following code:

    ```python
    import pygame
    pygame.init()

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Pygame Test')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    ```

3. Run the script:

    ```bash
    python3 pygame_test.py
    ```

If a window opens, Pygame is installed correctly.

---

## Step 4: Deactivate Virtual Environment (Optional)

When finished, deactivate the virtual environment:

```bash
deactivate
```

---

This setup ensures Pygame is installed and running correctly on your Raspberry Pi.
