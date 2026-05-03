from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers.params import HEADERS

# Other Persistent session to avoid lockouts
def configure_driver():
    """Configurer et retourner un driver Selenium avec les entêtes personnalisées."""
    options = Options()
    options.add_argument('--headless')                              # Use standard headless mode
    options.add_argument('--disable-gpu')                           # Disable GPU
    options.add_argument('--disable-software-rasterizer')           # Prevent software fallback
    options.add_argument('--disable-webgl')                         # Disable WebGL
    options.add_argument('--disable-accelerated-2d-canvas')         # Disable graphics acceleration
    options.add_argument('--disable-accelerated-video-decode')      # Disable video acceleration
    options.add_argument('--ignore-gpu-blocklist')                  # Ignore GPU blacklist
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")     # Add a custom User-Agent
    driver = webdriver.Chrome(options=options)
    return driver