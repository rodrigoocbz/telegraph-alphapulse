# SCRIPT AUTOMÁTICO DE DEMO EN VÍDEO PARA ALPHAPULSE SWARM
# Objetivo: Generar un vídeo MP4 de demostración automatizado navegando por el dashboard Streamlit

import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def record_automated_demo():
    print("[*] Iniciando grabación automatizada de AlphaPulse Swarm...")
    os.makedirs("demo_output", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Grabación directa en formato de vídeo con Playwright
        context = browser.new_context(
            record_video_dir="demo_output/",
            record_video_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        print("[1/5] Abriendo dashboard Streamlit en http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(3)
        
        # Pestaña 1: Overview & Swarm Execution
        print("[2/5] Ejecutando análisis del Swarm...")
        page.screenshot(path="demo_output/step1_overview.png")
        # Scroll suave para mostrar el terminal
        page.mouse.wheel(0, 400)
        time.sleep(4)
        
        # Pestaña 2: Evaluadores y Consenso
        print("[3/5] Mostrando Evaluadores WASM y Slashing...")
        tabs = page.query_selector_all("button[data-baseweb='tab']")
        if len(tabs) >= 2:
            tabs[1].click()
            time.sleep(4)
            page.screenshot(path="demo_output/step2_evaluators.png")
            page.mouse.wheel(0, 300)
            time.sleep(3)
            
        # Pestaña 3: On-Chain EIP-712 Attestation
        print("[4/5] Mostrando firmas criptográficas EIP-712...")
        if len(tabs) >= 4:
            tabs[3].click()
            time.sleep(4)
            page.screenshot(path="demo_output/step3_attestation.png")
            page.mouse.wheel(0, 300)
            time.sleep(3)
            
        # Pestaña 4: Backtest
        print("[5/5] Mostrando Backtesting cuantitativo...")
        if len(tabs) >= 3:
            tabs[2].click()
            time.sleep(4)
            page.screenshot(path="demo_output/step4_backtest.png")
            time.sleep(3)
            
        context.close()
        browser.close()
        
        # Obtener el archivo .webm generado y convertir a .mp4 con ffmpeg
        video_files = [f for f in os.listdir("demo_output") if f.endswith(".webm")]
        if video_files:
            webm_path = os.path.join("demo_output", video_files[0])
            mp4_path = "demo_alphapulse_automated.mp4"
            print(f"[*] Convirtiendo {webm_path} a {mp4_path} con ffmpeg...")
            subprocess.run([
                "ffmpeg", "-y", "-i", webm_path,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-r", "30", mp4_path
            ], check=True)
            print(f"[✓] Vídeo de demostración generado con éxito: {mp4_path}")

if __name__ == "__main__":
    record_automated_demo()
