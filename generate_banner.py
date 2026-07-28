import os
import math
import base64
import urllib.request
from PIL import Image, ImageEnhance, ImageOps

def get_avatar_base64_and_dither_matrix(grid_size=16):
    avatar_path = "avatar.png"
    if not os.path.exists(avatar_path):
        try:
            urllib.request.urlretrieve("https://github.com/1ErayYavuz.png", avatar_path)
        except Exception as e:
            print("Could not download avatar:", e)

    img_b64 = ""
    dither_pixels = []

    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        # Load and process image for dithering grid
        img = Image.open(avatar_path).convert("RGBA")
        
        # Make background transparent if white or make square
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img_cropped = img.crop((left, top, left + min_dim, top + min_dim))
        
        # Enhance contrast
        gray = img_cropped.convert("L")
        enhancer = ImageEnhance.Contrast(gray)
        gray_enhanced = enhancer.enhance(1.4)
        
        # Resize to grid
        small = gray_enhanced.resize((grid_size, grid_size), Image.Resampling.LANCZOS)
        
        for r in range(grid_size):
            row_pixels = []
            for c in range(grid_size):
                val = small.getpixel((c, r))
                norm = val / 255.0  # 0.0 (dark) to 1.0 (bright)
                row_pixels.append(norm)
            dither_pixels.append(row_pixels)
            
    return img_b64, dither_pixels

def generate_svg(theme="dark"):
    is_dark = (theme == "dark")
    img_b64, dither_matrix = get_avatar_base64_and_dither_matrix(grid_size=14)
    
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
    accent_yellow = "#d29922" if is_dark else "#9a6700"
    terminal_header_bg = "#21262d" if is_dark else "#eaeea1"
    
    # Generate 14x14 dithered grid dots for avatar graphic based on 1ErayYavuz avatar pixels
    dots_svg = []
    grid_size = len(dither_matrix) if dither_matrix else 14
    
    for r in range(grid_size):
        for c in range(grid_size):
            cx = 48 + c * 15.5
            cy = 205 + r * 7.5
            
            val = dither_matrix[r][c] if dither_matrix else 0.5
            
            if is_dark:
                opacity = max(0.1, min(1.0, val * 1.1))
                radius = max(1.2, min(3.2, val * 3.5))
                fill = accent_cyan if val > 0.6 else (accent_blue if val > 0.35 else accent_purple)
            else:
                opacity = max(0.1, min(1.0, (1.0 - val) * 1.1))
                radius = max(1.2, min(3.2, (1.0 - val) * 3.5))
                fill = accent_blue if val < 0.4 else (accent_purple if val < 0.7 else accent_cyan)
            
            anim_delay = (r * 0.08 + c * 0.04)
            
            dot_str = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{fill}" opacity="{opacity:.2f}">'
            dot_str += f'<animate attributeName="opacity" values="{opacity:.2f};1.0;{opacity:.2f}" dur="3.5s" begin="{anim_delay:.2f}s" repeatCount="indefinite"/>'
            dot_str += f'</circle>'
            dots_svg.append(dot_str)
            
    dots_xml = "\n      ".join(dots_svg)

    avatar_image_tag = ""
    if img_b64:
        avatar_image_tag = f"""
    <!-- Actual User Avatar Image with Circular Clip Path -->
    <clipPath id="avatar-clip">
      <circle cx="155" cy="132" r="50" />
    </clipPath>
    <circle cx="155" cy="132" r="53" fill="url(#avatar-border-grad)" />
    <image href="data:image/png;base64,{img_b64}" x="105" y="82" width="100" height="100" clip-path="url(#avatar-clip)" />
        """

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

    <linearGradient id="avatar-border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{accent_blue}" />
      <stop offset="50%" stop-color="{accent_cyan}" />
      <stop offset="100%" stop-color="{accent_purple}" />
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

  <!-- LEFT PANEL: Profile Avatar & Animated Dither Matrix -->
  <g class="glow-box">
    <rect x="30" y="65" width="250" height="265" rx="10" fill="{card_bg}" stroke="{border_color}" stroke-width="1.5"/>
    <!-- Avatar Frame Header -->
    <rect x="30" y="65" width="250" height="26" rx="10" fill="{border_color}" opacity="0.4"/>
    <text x="45" y="82" font-family="'Fira Code', monospace" font-size="10" fill="{text_muted}">[GITHUB_AVATAR.DITHER]</text>
    
    {avatar_image_tag}

    <!-- Dither Matrix Dots below avatar -->
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
    print("Generated dark.svg successfully with user profile avatar.")

    light_svg = generate_svg("light")
    with open("assets/light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Generated light.svg successfully with user profile avatar.")

if __name__ == "__main__":
    main()
