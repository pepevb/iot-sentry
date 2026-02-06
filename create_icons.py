#!/usr/bin/env python3
"""
Crear iconos PNG para el menu bar y dashboard desde las definiciones SVG
"""

import os

# Iconos SVG extraídos del JSX
ICONS = {
    # Menu bar (22pt / 44px para Retina)
    "shield": {
        "svg": """<svg viewBox="0 0 24 24" width="44" height="44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L4 6v5c0 5.25 3.4 10.15 8 11.4 4.6-1.25 8-6.15 8-11.4V6l-8-4z" stroke="white" stroke-width="1.5" stroke-linejoin="round" opacity="0.4"/>
            <circle cx="12" cy="14" r="1" fill="white"/>
            <path d="M9.5 12a3.5 3.5 0 0 1 5 0" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
            <path d="M7.5 10a6.5 6.5 0 0 1 9 0" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
        </svg>""",
        "sizes": [44, 64, 128]
    },

    "shield_alert": {
        "svg": """<svg viewBox="0 0 24 24" width="44" height="44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L4 6v5c0 5.25 3.4 10.15 8 11.4 4.6-1.25 8-6.15 8-11.4V6l-8-4z" stroke="#FF6B6B" stroke-width="1.5" stroke-linejoin="round" opacity="0.6"/>
            <circle cx="12" cy="14" r="1" fill="#FF6B6B"/>
            <path d="M9.5 12a3.5 3.5 0 0 1 5 0" stroke="#FF6B6B" stroke-width="1.4" stroke-linecap="round"/>
            <path d="M7.5 10a6.5 6.5 0 0 1 9 0" stroke="#FF6B6B" stroke-width="1.4" stroke-linecap="round"/>
            <circle cx="18" cy="6" r="3" fill="#FF3B3B"/>
            <text x="18" y="7.5" font-size="4" fill="white" text-anchor="middle" font-weight="bold">!</text>
        </svg>""",
        "sizes": [44, 64, 128]
    },

    "radar": {
        "svg": """<svg viewBox="0 0 24 24" width="44" height="44" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="white" stroke-width="1.3" opacity="0.25"/>
            <circle cx="12" cy="12" r="6" stroke="white" stroke-width="1.3" opacity="0.4"/>
            <circle cx="12" cy="12" r="3" stroke="white" stroke-width="1.3" opacity="0.6"/>
            <circle cx="12" cy="12" r="1.2" fill="white"/>
            <path d="M12 12L18 6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
        </svg>""",
        "sizes": [44, 64, 128]
    },

    # Iconos adicionales para dashboard
    "network": {
        "svg": """<svg viewBox="0 0 24 24" width="64" height="64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="2.5" fill="#60A5FA"/>
            <circle cx="5" cy="6" r="1.8" fill="#60A5FA" opacity="0.7"/>
            <circle cx="19" cy="6" r="1.8" fill="#60A5FA" opacity="0.7"/>
            <circle cx="5" cy="18" r="1.8" fill="#60A5FA" opacity="0.7"/>
            <circle cx="19" cy="18" r="1.8" fill="#60A5FA" opacity="0.7"/>
            <line x1="10" y1="10.5" x2="6.5" y2="7.5" stroke="#60A5FA" stroke-width="1.3" opacity="0.5"/>
            <line x1="14" y1="10.5" x2="17.5" y2="7.5" stroke="#60A5FA" stroke-width="1.3" opacity="0.5"/>
            <line x1="10" y1="13.5" x2="6.5" y2="16.5" stroke="#60A5FA" stroke-width="1.3" opacity="0.5"/>
            <line x1="14" y1="13.5" x2="17.5" y2="16.5" stroke="#60A5FA" stroke-width="1.3" opacity="0.5"/>
        </svg>""",
        "sizes": [64, 128]
    },

    "signal": {
        "svg": """<svg viewBox="0 0 24 24" width="64" height="64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 20a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z" fill="#34D399"/>
            <path d="M8.5 16a5 5 0 0 1 7 0" stroke="#34D399" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M5.5 13a9 9 0 0 1 13 0" stroke="#34D399" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M2.5 10a13 13 0 0 1 19 0" stroke="#34D399" stroke-width="1.8" stroke-linecap="round"/>
        </svg>""",
        "sizes": [64, 128]
    },

    "alert": {
        "svg": """<svg viewBox="0 0 24 24" width="64" height="64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#F87171" stroke-width="1.5" opacity="0.3"/>
            <path d="M12 7v6" stroke="#F87171" stroke-width="2" stroke-linecap="round"/>
            <circle cx="12" cy="16.5" r="1" fill="#F87171"/>
        </svg>""",
        "sizes": [64, 128]
    },
}


def create_svg_file(name, svg_content):
    """Crear archivo SVG"""
    filepath = f"assets/{name}.svg"
    with open(filepath, 'w') as f:
        f.write(svg_content)
    print(f"✅ Creado: {filepath}")
    return filepath


def convert_svg_to_png(svg_path, png_path, size=44):
    """Convertir SVG a PNG usando cairosvg"""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=size,
            output_height=size
        )
        print(f"✅ Convertido: {png_path} ({size}x{size})")
        return True
    except ImportError:
        print("⚠️  cairosvg no está instalado")
        print("   Instalando: pip install cairosvg")
        import subprocess
        subprocess.run(["pip", "install", "cairosvg"])
        return convert_svg_to_png(svg_path, png_path, size)
    except Exception as e:
        print(f"❌ Error convirtiendo {svg_path}: {e}")
        return False


def main():
    print("🎨 Creando iconos para IoT Sentry\n")
    print("=" * 50)

    # Crear directorio assets si no existe
    os.makedirs("assets", exist_ok=True)

    # Crear archivos SVG y PNG en múltiples tamaños
    print("\n1️⃣ Creando iconos...")

    for name, config in ICONS.items():
        svg_content = config["svg"]
        sizes = config["sizes"]

        # Crear SVG
        svg_path = create_svg_file(name, svg_content)

        # Crear PNG en diferentes tamaños
        for size in sizes:
            if size == 44:
                # Tamaño por defecto (menu bar)
                png_path = svg_path.replace('.svg', '.png')
            else:
                # Otros tamaños (dashboard)
                png_path = svg_path.replace('.svg', f'_{size}.png')

            convert_svg_to_png(svg_path, png_path, size)

    print("\n" + "=" * 50)
    print("\n✅ ICONOS CREADOS")
    print("\n📁 Archivos generados:")
    print("\n   Menu Bar (44px):")
    print("   • assets/shield.png")
    print("   • assets/shield_alert.png")
    print("   • assets/radar.png")
    print("\n   Dashboard (64px, 128px):")
    print("   • assets/shield_64.png, shield_128.png")
    print("   • assets/network_64.png, network_128.png")
    print("   • assets/signal_64.png, signal_128.png")
    print("   • assets/alert_64.png, alert_128.png")
    print("\n💡 Uso:")
    print("   Menu bar: icon='assets/shield.png'")
    print("   Dashboard: QIcon('assets/shield_64.png')")


if __name__ == "__main__":
    main()
