# Installation Instructions

## Requirements

- Python 3.8+
- pygame

## Install Dependencies

```bash
pip install -r requirements.txt
```

Or directly:

```bash
pip install pygame
```

## Running the Application

```bash
python3 main.py
```

## Controls

- **Arrow Keys**: Move robot manually
- **D**: Toggle autonomous mode
- **S**: Sleep/dream (consolidate memory)
- **M**: Mirror test (self-recognition)
- **SPACE**: Pause/Resume
- **ESC**: Quit

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```