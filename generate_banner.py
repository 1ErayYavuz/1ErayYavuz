import os
import math
import urllib.request
from PIL import Image, ImageEnhance, ImageOps

def get_avatar_dither_matrix(grid_width=28, grid_height=28):
    avatar_path = "avatar.png"
    if not os.path.exists(avatar_path):
        try:
            urllib.request.urlretrieve("https://github.com/1ErayYavuz.png", avatar_path)
        except Exception as e:
            print("Could not download avatar:", e)

    dither_pixels = []

    if os.path.exists(avatar_path):
        img = Image.open(avatar_path).convert("RGB")
        
        # Square crop
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img_cropped = img.crop((left, top, left + min_dim, top + min_dim))
        
        # Convert to grayscale and boost contrast for sharp dither portrait
        gray = img_cropped.convert("L")
        gray = ImageOps.autocontrast(gray, cutoff=2)
        enhancer = ImageEnhance.Contrast(gray)
        gray_enhanced = enhancer.enhance(1.6)
        
        # Resize to grid size
        small = gray_enhanced.resize((grid_width, grid_height), Image.Resampling.LANCZOS)
        
        # Optional Floyd-Steinberg Dithering for binary contrast
        dithered_img = small.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
        
        for r in range(grid_height):
            row_pixels = []
            for c in range(grid_width):
                val_gray = small.getpixel((c, r)) / 255.0
                val_binary = 1.0 if dithered_img.getpixel((c, r)) > 0 else 0.0
                # Combine grayscale luminance and dither binary value
                combined = (val_gray * 0.4) + (val_binary * 0.6)
                row_pixels.append(combined)
            dither_pixels.append(row_pixels)
            
    return dither_pixels

def generate_svg(theme="dark"):
    is_dark = (theme == "dark")
    grid_w, grid_h = 28, 28
    dither_matrix = get_avatar_dither_matrix(grid_w, grid_h)
    
    # Color palette definitions
    bg_color = "#0d1117" if is_dark else "#ffffff"
    card_bg = "#161b22" if is_dark else "#f6f8fa"
    border_color = "#30363d" if is_dark else "#d0d7de"
    text_main = "#c9d1d9" if is_dark else "#24292f"
    text_muted = "#8b949e" if is_dark else "#57606a"
    accent_green = "#3fb950" if is_dark else "#1a7f37"
    accent_blue = "#58a6ff" if is_dark else "#0969da"
    accent_purple = "#bc8cff" if is_dark else "#8250df"
    accent_cyan = "#39c5bb" if is_dark else "#1b7c83"
    accent_white = "#f0f6fc" if is_dark else "#1f2328"
    terminal_header_bg = "#21262d" if is_dark else "#eaeea1"
    
    # Generate 28x28 dithered grid dots representing 1ErayYavuz avatar photo
    dots_svg = []
    
    box_x = 42
    box_y = 100
    spacing_x = 8.0
    spacing_y = 7.5
    
    for r in range(grid_h):
        for c in range(grid_w):
            cx = box_x + c * spacing_x
            cy = box_y + r * spacing_y
            
            val = dither_matrix[r][c] if dither_matrix else 0.5
            
            if is_dark:
                # Dark mode: higher luminance/binary -> brighter dot
                opacity = max(0.12, min(1.0, val * 1.2))
                radius = max(0.8, min(2.8, val * 3.0))
                
                if val > 0.75:
                    fill = accent_white
                elif val > 0.5:
                    fill = accent_cyan
                elif val > 0.3:
                    fill = accent_blue
                else:
                    fill = accent_purple
            else:
                # Light mode: darker pixels in photo -> darker, bolder dots
                inv_val = 1.0 - val
                opacity = max(0.12, min(1.0, inv_val * 1.2))
                radius = max(0.8, min(2.8, inv_val * 3.0))
                
                if inv_val > 0.75:
                    fill = accent_white
                elif inv_val > 0.5:
                    fill = accent_blue
                elif inv_val > 0.3:
                    fill = accent_purple
                else:
                    fill = accent_cyan
            
            anim_delay = ((r % 5) * 0.12 + (c % 5) * 0.08)
            
            dot_str = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{fill}" opacity="{opacity:.2f}">'
            if val > 0.2:
                dot_str += f'<animate attributeName="opacity" values="{opacity:.2f};{min(1.0, opacity+0.3):.2f};{opacity:.2f}" dur="3s" begin="{anim_delay:.2f}s" repeatCount="indefinite"/>'
            dot_str += f'</circle>'
            dots_svg.append(dot_str)
            
    dots_xml = "\n      ".join(dots_svg)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 360" width="100%" height="100%">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&amp;family=Inter:wght@400;600;700&amp;display=swap');
      
      .terminal-bg {{ fill: {bg_color}; rx: 12px; ry: 12px; stroke: {border_color}; stroke-width: 1.5px; }}
      .header-bg {{ fill: {terminal_header_bg}; rx: 12px; ry: 12px; }}
      .title-text {{ font-family: 'Fira Code', monospace; font-size: 13px; fill: {text_muted}; font-weight: 500; }}
      .cmd-text {{ font-family: 'Fira Code', monospace; font-size: 14px; fill: {accent_green}; font-weight: 600; }}
      .prompt-user {{ fill: {accent_blue}; }}
      .prompt-host {{ fill: {accent_purple}; }}
      .label-text {{ font-family: 'Fira Code', monospace; font-size: 13px; fill: {accent_blue}; font-weight: 600; }}
      .val-text {{ font-family: 'Inter', sans-serif; font-size: 13px; fill: {text_main}; font-weight: 500; }}
      .val-bold {{ font-weight: 700; fill: {accent_cyan}; }}
      .badge-text {{ font-family: 'Fira Code', monospace; font-size: 11px; fill: {accent_purple}; font-weight: 600; }}
      
      /* Animations */
      .shimmer {{
        stroke: url(#shimmer-grad);
        stroke-width: 2;
        fill: none;
        stroke-dasharray: 200 800;
        animation: shimmer-anim 6s infinite linear;
      }}
      
      @keyframes shimmer-anim {{
        0% {{ stroke-dashoffset: 1000; }}
        100% {{ stroke-dashoffset: 0; }}
      }}
      
      .cursor {{
        fill: {accent_green};
        animation: blink 1s infinite;
      }}
      
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
      }}
      
      .glow-box {{
        filter: drop-shadow(0px 0px 8px {accent_blue}44);
      }}
    </style>
    
    <linearGradient id="shimmer-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent_blue}" stop-opacity="0" />
      <stop offset="50%" stop-color="{accent_cyan}" stop-opacity="1" />
      <stop offset="100%" stop-color="{accent_purple}" stop-opacity="0" />
    </linearGradient>
  </defs>

  <!-- Outer Window Container -->
  <rect x="2" y="2" width="876" height="356" class="terminal-bg" />
  
  <!-- Header Bar -->
  <path d="M 2,14 Q 2,2 14,2 L 866,2 Q 878,2 878,14 L 878,42 L 2,42 Z" fill="{terminal_header_bg}" stroke="{border_color}" stroke-width="1" />
  
  <!-- Window Control Buttons -->
  <circle cx="24" cy="22" r="6" fill="#ff5f56" />
  <circle cx="44" cy="22" r="6" fill="#ffbd2e" />
  <circle cx="64" cy="22" r="6" fill="#27c93f" />
  
  <!-- Window Title -->
  <text x="440" y="26" text-anchor="middle" class="title-text">eray@1ErayYavuz:~ (zsh)</text>
  
  <!-- Shimmer Border Line -->
  <rect x="2" y="2" width="876" height="356" rx="12" ry="12" class="shimmer" />

  <!-- LEFT PANEL: Pure Dithered Dot Matrix Portrait -->
  <g class="glow-box">
    <rect x="30" y="65" width="250" height="265" rx="10" fill="{card_bg}" stroke="{border_color}" stroke-width="1.5"/>
    
    <!-- Avatar Frame Header -->
    <rect x="30" y="65" width="250" height="26" rx="10" fill="{border_color}" opacity="0.4"/>
    <text x="45" y="82" font-family="'Fira Code', monospace" font-size="10" fill="{text_muted}">[DITHERED_PORTRAIT_MATRIX]</text>

    <!-- 28x28 Dot Matrix Portrait derived from GitHub avatar -->
    {dots_xml}
    
    <text x="155" y="320" text-anchor="middle" class="badge-text">STATUS: ONLINE ⚡</text>
  </g>

  <!-- RIGHT PANEL: Neofetch / Terminal System Info -->
  <!-- Prompt Line 1 -->
  <text x="310" y="85" class="cmd-text">
    <tspan class="prompt-user">1ErayYavuz</tspan><tspan fill="{text_muted}">@</tspan><tspan class="prompt-host">github-shell</tspan><tspan fill="{text_main}">:~$ </tspan><tspan fill="{text_main}">neofetch --user 1ErayYavuz</tspan>
  </text>
  
  <!-- Separator line -->
  <line x1="310" y1="100" x2="840" y2="100" stroke="{border_color}" stroke-width="1" stroke-dasharray="4 4" />

  <!-- Info Fields -->
  <g transform="translate(310, 125)">
    <!-- User Field -->
    <text x="0" y="0" class="label-text">USER      <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="0" class="val-text val-bold">Eray Yavuz (@1ErayYavuz)</text>

    <!-- Role Field -->
    <text x="0" y="30" class="label-text">ROLE      <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="30" class="val-text">Software Engineer &amp; Full-Stack Developer</text>

    <!-- Focus Field -->
    <text x="0" y="60" class="label-text">FOCUS     <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="60" class="val-text">Modern Web Apps, Cloud &amp; High Performance Systems</text>

    <!-- Stack Field -->
    <text x="0" y="90" class="label-text">STACK     <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="90" class="val-text">TypeScript, React, Next.js, Node.js, Python, Tailwind</text>

    <!-- Shell / OS -->
    <text x="0" y="120" class="label-text">SYSTEM    <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="120" class="val-text">Arch Linux x86_64 / zsh 5.9</text>

    <!-- Uptime -->
    <text x="0" y="150" class="label-text">UPTIME    <tspan fill="{text_muted}">::</tspan></text>
    <text x="120" y="150" class="val-text" fill="{accent_green}">99.9% (Continuous Learning &amp; Building)</text>
  </g>

  <!-- Prompt Line 2 / Command Cursor -->
  <text x="310" y="315" class="cmd-text">
    <tspan class="prompt-user">1ErayYavuz</tspan><tspan fill="{text_muted}">@</tspan><tspan class="prompt-host">github-shell</tspan><tspan fill="{text_main}">:~$ </tspan><tspan fill="{accent_cyan}">echo $MOTD</tspan>
    <rect x="525" y="303" width="8" height="15" class="cursor" />
  </text>
  
  <text x="310" y="335" font-family="'Fira Code', monospace" font-size="12" fill="{text_muted}">
    "Building scalable solutions &amp; sleek user experiences."
  </text>
</svg>
"""
    return svg_content

def main():
    os.makedirs("assets", exist_ok=True)
    
    dark_svg = generate_svg("dark")
    with open("assets/dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print("Generated pure dithered dot matrix portrait dark.svg successfully.")

    light_svg = generate_svg("light")
    with open("assets/light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Generated pure dithered dot matrix portrait light.svg successfully.")

if __name__ == "__main__":
    main()
