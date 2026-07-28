import os
import math

def generate_svg(theme="dark"):
    is_dark = (theme == "dark")
    
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
    
    # Generate 16x16 dithered grid dots for avatar graphic
    dots_svg = []
    grid_size = 14
    for r in range(grid_size):
        for c in range(grid_size):
            cx = 45 + c * 16
            cy = 115 + r * 16
            # Distances to form a stylized "E" or geometric avatar shape
            dist_center = math.sqrt((r - 6.5)**2 + (c - 6.5)**2)
            opacity = max(0.15, min(1.0, 1.0 - (dist_center / 8.0)))
            
            # Pattern logic for futuristic tech core shape
            is_core = (c in [2, 3] and 2 <= r <= 11) or (r in [2, 6, 11] and 2 <= c <= 11)
            
            fill = accent_cyan if is_core else (accent_blue if (r + c) % 2 == 0 else accent_purple)
            anim_delay = (r * 0.1 + c * 0.05)
            
            dot_str = f'<circle cx="{cx}" cy="{cy}" r="{3.5 if is_core else 2.5}" fill="{fill}" opacity="{opacity:.2f}">'
            dot_str += f'<animate attributeName="opacity" values="{opacity:.2f};1.0;{opacity:.2f}" dur="3s" begin="{anim_delay:.2f}s" repeatCount="indefinite"/>'
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

    <linearGradient id="avatar-border" x1="0%" y1="0%" x2="100%" y2="100%">
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

  <!-- LEFT PANEL: Animated Dither Avatar Matrix -->
  <g class="glow-box">
    <rect x="30" y="65" width="250" height="265" rx="10" fill="{card_bg}" stroke="{border_color}" stroke-width="1.5"/>
    <!-- Avatar Frame Header -->
    <rect x="30" y="65" width="250" height="30" rx="10" fill="{border_color}" opacity="0.4"/>
    <text x="45" y="85" font-family="'Fira Code', monospace" font-size="11" fill="{text_muted}">[SYSTEM_AVATAR.DITHER]</text>
    
    <!-- Matrix Dots -->
    {dots_xml}
    
    <text x="155" y="315" text-anchor="middle" class="badge-text">STATUS: ONLINE ⚡</text>
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
    print("Generated dark.svg successfully.")

    light_svg = generate_svg("light")
    with open("assets/light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Generated light.svg successfully.")

if __name__ == "__main__":
    main()
