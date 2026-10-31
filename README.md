# ZenWalk

ZenWalk is a personal-safety and walking-companion mobile app prototype built with Python and Kivy. It combines a simple step-tracker dashboard with a three-level safety status system (Green / Yellow / Red) that can send your live location to trusted emergency contacts with a single tap.

The idea: when you're walking alone, you shouldn't have to fumble through your phone to ask for help. ZenWalk puts "I'm safe", "I'm unsure" and "I'm in danger" one tap away. The step tracker UI ensures your potential attacker is not alerted of the fact that you are trying to get help.

## Features

- **Onboarding / profile registration:** on first launch, enter your name, phone number, age, up to 5 emergency contacts, a home address and up to 3 optional other addresses (office, college, other).
- **Profile management:** view and edit your saved details at any time from the dashboard.
- **Step tracker dashboard:** shows a "Steps Today" counter (currently simulated with a +100 button).
- **Safety alerts:**
  - 🟢 **Safe (Green):** marks you as safe, no action taken.
  - 🟡 **Unsure (Yellow):** composes an SMS asking contacts to stay alert and check in, including a Google Maps link to your location.
  - 🔴 **Danger (Red):** composes an SMS saying you are in danger and asking contacts to call emergency services, including your location link.
- **Location sharing:** uses GPS (via Plyer) to build a Google Maps link; falls back to a default location when GPS isn't available (e.g. on desktop).
- **Maps shortcut:** opens Google Maps at a preset "safe space" location.
- **Local storage:** all profile data is stored on the device in a SQLite database.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Kivy | Cross-platform UI framework (screens, layouts, buttons, popups) |
| Plyer | Access to device GPS for location |
| SQLite (`sqlite3`) | Local on-device storage of the user profile |
| `webbrowser` (Python standard library) | Opens `sms:` links and Google Maps URLs |
| `urllib.parse` (Python standard library) | URL-encoding alert messages for SMS links |
| Google Maps URLs | Shareable location links |

## Demo Videos

- [Demo video 1](https://drive.google.com/file/d/1nwluYrgI9Be9ggdpJ3fPaUDpAq0Uq8_E/view?usp=sharing)
- [Demo video 2](https://drive.google.com/file/d/1tTTzP0IAtQX6A21zMa8qQidPxOHyQvgm/view?usp=sharing)
