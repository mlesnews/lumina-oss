# LUMINA Footer Ticker Banner

**Part of LUMINA Core**

Airport ticker / LED sign effect for Cursor IDE footer.

## Features

- Slow horizontal scrolling through all footer items
- LED sign aesthetic with smooth animation
- Pause on hover/click
- Configurable speed and spacing
- All footer items visible in rotation

## Installation

1. Copy this extension to your Cursor IDE extensions folder
2. Run `npm install` in the extension directory
3. Run `npm run compile` to build
4. Reload Cursor IDE

## Configuration

Edit `config/footer_ticker_config.json in your LUMINA project:

```json
{
  "scroll_speed": 30,
  "item_spacing": 50,
  "pause_on_hover": true,
  "items": [...]
}
```

Or use Cursor settings:
- `lumina.footerTicker.enabled` - Enable/disable ticker
- `lumina.footerTicker.scrollSpeed` - Scroll speed (pixels/second)
- `lumina.footerTicker.itemSpacing` - Item spacing (pixels)
- `lumina.footerTicker.pauseOnHover` - Pause on hover

## Usage

The ticker automatically starts when Cursor IDE loads. Click the ticker to pause/resume.

## Tags

#JARVIS @LUMINA #CURSOR #FOOTER #TICKER #BANNER #LUMINA_CORE
