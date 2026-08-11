#!/usr/bin/env python3
"""
ChatGPT Web Relay for Hermes Agent.

Controls ChatGPT web UI (chatgpt.com) via Playwright with persistent Chrome profile.
Enables Hermes to use ChatGPT web features without API quota consumption.

Usage:
    from chatgpt_web_relay import ChatGPTWebRelay
    
    relay = ChatGPTWebRelay()
    result = relay.ask("分析這個問題", model="gpt-5.5-pro-extended")
    print(result["text"])
    relay.close()
"""

import os
import sys
import time
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from contextlib import contextmanager

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright
    from playwright_stealth import stealth_sync
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip3 install playwright playwright-stealth")
    print("Then: python3 -m playwright install chromium")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "user_data_dir": "~/.hermes/browser_profiles/chatgpt_relay",
    "channel": "chrome",  # "chrome" for real Chrome, None for bundled Chromium
    "headless": False,
    "stealth": True,
    "disable_blink_features": True,
    "default_model": "gpt-5.5-pro-extended",
    "default_effort": "high",
    "navigation_timeout": 60000,
    "response_timeout": 300000,  # 5 minutes for Deep Research
    "chatgpt_url": "https://chatgpt.com",
    "debug": False,
}

MODEL_MAP = {
    "gpt-5.5-pro-extended": ["GPT-5.5 Pro Extended", "5.5 Pro Extended"],
    "gpt-5.4-thinking-light": ["GPT-5.4 Thinking Light", "5.4 Thinking Light"],
    "deep-research": ["Deep Research", "深度研究"],
    "gpt-4o": ["GPT-4o", "4o"],
    "gpt-4o-mini": ["GPT-4o mini", "4o mini"],
    "o1-pro": ["o1 Pro", "o1-Pro"],
    "o1": ["o1", "o1-preview"],
}

# ──────────────────────────────────────────────────────────────────────────────
# Data Classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RelayResult:
    """Result from a ChatGPT web interaction."""
    text: str = ""
    images: List[str] = field(default_factory=list)
    conversation_url: str = ""
    model_used: str = ""
    success: bool = True
    error: str = ""
    raw_html: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "images": self.images,
            "conversation_url": self.conversation_url,
            "model_used": self.model_used,
            "success": self.success,
            "error": self.error,
        }
    
    def __str__(self):
        return f"RelayResult(success={self.success}, text_len={len(self.text)}, images={len(self.images)}, url={self.conversation_url[:50] if self.conversation_url else 'none'}...)"


# ──────────────────────────────────────────────────────────────────────────────
# Main Relay Class
# ──────────────────────────────────────────────────────────────────────────────

class ChatGPTWebRelay:
    """
    Controls ChatGPT web UI via Playwright.
    
    Uses a persistent Chrome profile to maintain login state across sessions.
    """
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        Initialize the relay.
        
        Args:
            config_path: Path to YAML config file
            **kwargs: Override config values directly
        """
        self.config = self._load_config(config_path, kwargs)
        self._setup_logging()
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._initialized = False
        self._current_model = self.config["default_model"]
        
    def _load_config(self, config_path: Optional[str], overrides: Dict) -> Dict:
        config = DEFAULT_CONFIG.copy()
        
        if config_path:
            path = Path(os.path.expanduser(config_path))
            if path.exists():
                with open(path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                    config.update(file_config)
        
        config.update(overrides)
        
        # Expand user path
        config["user_data_dir"] = os.path.expanduser(config["user_data_dir"])
        
        return config
    
    def _setup_logging(self):
        level = logging.DEBUG if self.config["debug"] else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ChatGPTWebRelay")
    
    def _launch_browser(self) -> None:
        """Launch browser with persistent context."""
        if self._initialized:
            return
            
        self.logger.info("Launching browser...")
        
        self.playwright = sync_playwright().start()
        
        # Browser launch arguments
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-web-security",  # Sometimes needed for file uploads
            "--allow-running-insecure-content",
        ]
        
        if self.config["disable_blink_features"]:
            launch_args.append("--disable-blink-features=AutomationControlled")
        
        # Launch with persistent context
        if self.config["channel"] == "chrome":
            # Use real Chrome - better for Cloudflare/Turnstile
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.config["user_data_dir"],
                channel="chrome",
                headless=self.config["headless"],
                args=launch_args,
                viewport={"width": 1920, "height": 1080},
                screen={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="America/Los_Angeles",
                extra_http_headers={
                    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                },
                ignore_https_errors=True,
            )
        else:
            # Bundled Chromium
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.config["user_data_dir"],
                headless=self.config["headless"],
                args=launch_args,
                viewport={"width": 1920, "height": 1080},
                ignore_https_errors=True,
            )
        
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        
        # Apply stealth if enabled
        if self.config["stealth"]:
            try:
                stealth_sync(self.page)
                self.logger.debug("Stealth applied")
            except Exception as e:
                self.logger.warning(f"Stealth failed: {e}")
        
        # Add init script for additional fingerprint spoofing
        self.page.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Chrome runtime
            window.chrome = { runtime: {} };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            
            // Plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(() => ({ name: 'Chrome PDF Plugin' }))
            });
        """)
        
        self._initialized = True
        self.logger.info("Browser launched successfully")
    
    def _ensure_page(self) -> Page:
        """Ensure we have a valid page, create if needed."""
        if not self.page or self.page.is_closed():
            if self.context:
                self.page = self.context.new_page()
            else:
                self._launch_browser()
        return self.page
    
    def _navigate_to_chatgpt(self) -> None:
        """Navigate to ChatGPT and wait for load."""
        page = self._ensure_page()
        
        self.logger.info("Navigating to ChatGPT...")
        page.goto(
            self.config["chatgpt_url"],
            wait_until="networkidle",
            timeout=self.config["navigation_timeout"]
        )
        
        # Wait for the main app to load
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)  # Let React hydrate
        
        # Check if we need to login (shouldn't happen with persistent profile)
        if "login" in page.url or "auth" in page.url:
            self.logger.warning("Not logged in! Please log in manually in the browser window.")
            self.logger.info("Waiting for manual login... (press Enter in terminal when done)")
            input("Press Enter after logging in...")
            page.goto(self.config["chatgpt_url"], wait_until="networkidle")
    
    def initialize(self) -> None:
        """Initialize browser and navigate to ChatGPT."""
        if self._initialized and self.page and not self.page.is_closed():
            return
        self._launch_browser()
        self._navigate_to_chatgpt()
    
    # ──────────────────────────────────────────────────────────────────────────
    # Core Interaction Methods
    # ──────────────────────────────────────────────────────────────────────────
    
    def _find_prompt_textarea(self) -> Any:
        """Find the prompt textarea with multiple selector fallbacks."""
        page = self._ensure_page()
        
        selectors = [
            'textarea#prompt-textarea',
            'textarea[data-id="root"]',
            'div.ProseMirror[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="Ask"]',
            'textarea[placeholder*="詢問"]',
            'textarea[placeholder*="輸入"]',
            'div[contenteditable="true"][data-placeholder]',
        ]
        
        for sel in selectors:
            try:
                locator = page.locator(sel).first
                if locator.count() > 0 and locator.is_visible():
                    self.logger.debug(f"Found prompt textarea: {sel}")
                    return locator
            except:
                continue
        
        raise RuntimeError("Could not find prompt textarea")
    
    def _find_send_button(self) -> Any:
        """Find the send button with fallbacks."""
        page = self._ensure_page()
        
        selectors = [
            'button[data-testid="send-button"]',
            'button:has-text("Send")',
            'button:has-text("發送")',
            'button[aria-label*="Send"]',
            'button[aria-label*="發送"]',
            'button[type="submit"]',
        ]
        
        for sel in selectors:
            try:
                locator = page.locator(sel).first
                if locator.count() > 0 and locator.is_visible():
                    return locator
            except:
                continue
        
        raise RuntimeError("Could not find send button")
    
    def _wait_for_response_complete(self, timeout: int = None) -> None:
        """Wait for the assistant response to finish streaming."""
        page = self._ensure_page()
        timeout = timeout or self.config["response_timeout"]
        
        self.logger.debug("Waiting for response to complete...")
        
        # Strategy 1: Wait for "Stop generating" button to disappear
        stop_selectors = [
            'button[data-testid="stop-button"]',
            'button:has-text("Stop generating")',
            'button:has-text("停止生成")',
            'button[aria-label*="Stop"]',
        ]
        
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            stopped = True
            for sel in stop_selectors:
                try:
                    if page.locator(sel).first.is_visible():
                        stopped = False
                        break
                except:
                    pass
            
            if stopped:
                # Also check network idle
                try:
                    page.wait_for_load_state("networkidle", timeout=2000)
                except:
                    pass
                self.logger.debug("Response appears complete")
                return
            
            time.sleep(0.5)
        
        self.logger.warning(f"Response timeout after {timeout}ms")
    
    def _extract_response(self) -> RelayResult:
        """Extract the assistant's response from the page."""
        page = self._ensure_page()
        
        result = RelayResult()
        
        # Get conversation URL
        result.conversation_url = page.url
        
        # Find the last assistant message
        response_selectors = [
            'div[data-message-author-role="assistant"]',
            'div.message-assistant',
            'div[data-testid="conversation-turn-3"]',  # varies
            '.markdown.prose',
            'article[data-message-author-role="assistant"]',
        ]
        
        last_response = None
        for sel in response_selectors:
            try:
                elements = page.locator(sel).all()
                if elements:
                    last_response = elements[-1]  # Last assistant message
                    break
            except:
                continue
        
        if last_response:
            # Get text content
            try:
                result.text = last_response.inner_text()
            except:
                try:
                    result.text = last_response.text_content()
                except:
                    result.text = ""
            
            # Get HTML for debugging
            try:
                result.raw_html = last_response.inner_html()
            except:
                pass
            
            # Extract images
            try:
                images = last_response.locator('img').all()
                for img in images:
                    src = img.get_attribute("src")
                    if src and ("files.oaiusercontent.com" in src or "dalle" in src or "image" in src):
                        result.images.append(src)
            except:
                pass
        
        # Also check for image generation results in the page
        try:
            gen_images = page.locator('img[data-testid="image-generation-result"]').all()
            for img in gen_images:
                src = img.get_attribute("src")
                if src and src not in result.images:
                    result.images.append(src)
        except:
            pass
        
        result.success = len(result.text) > 0 or len(result.images) > 0
        return result
    
    def _send_prompt(self, prompt: str) -> None:
        """Send a prompt to ChatGPT."""
        page = self._ensure_page()
        
        # Find and fill textarea
        textarea = self._find_prompt_textarea()
        
        # Clear and fill
        try:
            textarea.clear()
        except:
            # For contenteditable div
            page.evaluate('el => el.innerText = ""', textarea.element_handle())
        
        # Fill with prompt - use keyboard for contenteditable
        if "contenteditable" in (textarea.get_attribute("contenteditable") or ""):
            textarea.click()
            page.keyboard.type(prompt, delay=10)
        else:
            textarea.fill(prompt)
        
        time.sleep(0.5)
        
        # Click send
        send_btn = self._find_send_button()
        send_btn.click()
        
        self.logger.debug("Prompt sent, waiting for response...")
    
    def _switch_model(self, model_id: str, effort: str = "high") -> bool:
        """Switch the model in ChatGPT UI."""
        page = self._ensure_page()
        
        model_names = MODEL_MAP.get(model_id, [model_id])
        
        self.logger.info(f"Switching model to: {model_id} (effort: {effort})")
        
        # Click model switcher
        switcher_selectors = [
            'button[data-testid="model-switcher"]',
            'button:has-text("GPT")',
            'button[aria-label*="Model"]',
            'button[aria-label*="模型"]',
            'div[role="button"]:has-text("GPT")',
        ]
        
        clicked = False
        for sel in switcher_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click()
                    clicked = True
                    break
            except:
                continue
        
        if not clicked:
            self.logger.error("Could not find model switcher")
            return False
        
        time.sleep(1)
        
        # Click the desired model
        for name in model_names:
            try:
                option_selectors = [
                    f'div[role="option"]:has-text("{name}")',
                    f'button:has-text("{name}")',
                    f'li:has-text("{name}")',
                    f'[data-testid*="model"]:has-text("{name}")',
                ]
                for opt_sel in option_selectors:
                    try:
                        opt = page.locator(opt_sel).first
                        if opt.count() > 0 and opt.is_visible():
                            opt.click()
                            self.logger.info(f"Selected model: {name}")
                            time.sleep(1)
                            # Handle effort selection for thinking models
                            if "thinking" in model_id.lower() or "pro" in model_id.lower():
                                self._select_effort(effort)
                            return True
                    except:
                        continue
            except:
                continue
        
        self.logger.error(f"Could not find model option for: {model_id}")
        return False
    
    def _select_effort(self, effort: str) -> None:
        """Select thinking effort level."""
        page = self._ensure_page()
        
        effort_map = {
            "low": ["Low", "低", "輕度"],
            "medium": ["Medium", "中", "中度"],
            "high": ["High", "高", "深度"],
        }
        
        efforts = effort_map.get(effort, [effort])
        
        for eff in efforts:
            try:
                selectors = [
                    f'button:has-text("{eff}")',
                    f'div[role="option"]:has-text("{eff}")',
                    f'[data-testid*="effort"]:has-text("{eff}")',
                ]
                for sel in selectors:
                    try:
                        btn = page.locator(sel).first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click()
                            self.logger.debug(f"Selected effort: {eff}")
                            return
                    except:
                        continue
            except:
                continue
    
    def _upload_file(self, file_path: str) -> bool:
        """Upload a file to ChatGPT."""
        page = self._ensure_page()
        
        # Find file upload button
        upload_selectors = [
            'button[data-testid="attach-files"]',
            'button[aria-label*="Attach"]',
            'button[aria-label*="附件"]',
            'button:has-text("Attach")',
            'button:has-text("上傳")',
        ]
        
        for sel in upload_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click()
                    break
            except:
                continue
        else:
            self.logger.error("Could not find file upload button")
            return False
        
        time.sleep(0.5)
        
        # Find file input
        file_input = page.locator('input[type="file"]').first
        if file_input.count() == 0:
            self.logger.error("File input not found")
            return False
        
        # Set file
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        file_input.set_input_files(abs_path)
        
        self.logger.info(f"File uploaded: {abs_path}")
        time.sleep(2)  # Wait for upload processing
        return True
    
    def _start_new_chat(self) -> None:
        """Start a new conversation."""
        page = self._ensure_page()
        
        new_chat_selectors = [
            'a[href="/"]:has-text("New chat")',
            'button:has-text("New chat")',
            'button:has-text("新對話")',
            'a[data-testid="new-chat"]',
            'button[data-testid="new-chat"]',
        ]
        
        for sel in new_chat_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click()
                    time.sleep(1)
                    self.logger.info("Started new chat")
                    return
            except:
                continue
        
        # Fallback: navigate to base URL
        page.goto(self.config["chatgpt_url"], wait_until="networkidle")
        time.sleep(2)
    
    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────
    
    def ask(
        self,
        prompt: str,
        model: Optional[str] = None,
        effort: Optional[str] = None,
        new_chat: bool = False
    ) -> RelayResult:
        """
        Send a prompt to ChatGPT and get the response.
        
        Args:
            prompt: The prompt to send
            model: Model ID (e.g., "gpt-5.5-pro-extended", "deep-research")
            effort: Thinking effort ("low", "medium", "high")
            new_chat: Start a new conversation first
            
        Returns:
            RelayResult with text, images, conversation_url
        """
        self.initialize()
        
        model = model or self.config["default_model"]
        effort = effort or self.config["default_effort"]
        
        if new_chat or self._current_model != model:
            self._start_new_chat()
            if model != self.config["default_model"]:
                self._switch_model(model, effort)
            self._current_model = model
        
        try:
            self._send_prompt(prompt)
            self._wait_for_response_complete()
            result = self._extract_response()
            result.model_used = model
            return result
        except Exception as e:
            self.logger.error(f"Error in ask: {e}")
            return RelayResult(success=False, error=str(e))
    
    def deep_research(self, topic: str, model: str = "deep-research") -> RelayResult:
        """
        Start a Deep Research task and wait for completion.
        
        Args:
            topic: Research topic
            model: Should be "deep-research"
            
        Returns:
            RelayResult with the research report
        """
        # Deep Research takes much longer
        original_timeout = self.config["response_timeout"]
        self.config["response_timeout"] = 600000  # 10 minutes
        
        try:
            result = self.ask(topic, model=model, new_chat=True)
            return result
        finally:
            self.config["response_timeout"] = original_timeout
    
    def ask_with_image(
        self,
        prompt: str,
        image_path: str,
        model: Optional[str] = None,
        effort: Optional[str] = None
    ) -> RelayResult:
        """
        Send a prompt with an image attachment.
        
        Args:
            prompt: Text prompt
            image_path: Path to image file
            model: Model to use
            effort: Thinking effort
            
        Returns:
            RelayResult
        """
        self.initialize()
        
        if not os.path.exists(os.path.expanduser(image_path)):
            return RelayResult(success=False, error=f"Image not found: {image_path}")
        
        # Upload image first
        if not self._upload_file(image_path):
            return RelayResult(success=False, error="Failed to upload image")
        
        # Then send prompt
        return self.ask(prompt, model=model, effort=effort)
    
    def ask_with_file(
        self,
        prompt: str,
        file_path: str,
        model: Optional[str] = None,
        effort: Optional[str] = None
    ) -> RelayResult:
        """
        Send a prompt with a file attachment (PDF, code, etc.).
        
        Args:
            prompt: Text prompt
            file_path: Path to file
            model: Model to use
            effort: Thinking effort
            
        Returns:
            RelayResult
        """
        self.initialize()
        
        if not os.path.exists(os.path.expanduser(file_path)):
            return RelayResult(success=False, error=f"File not found: {file_path}")
        
        if not self._upload_file(file_path):
            return RelayResult(success=False, error="Failed to upload file")
        
        return self.ask(prompt, model=model, effort=effort)
    
    def switch_model(self, model: str, effort: str = "high") -> bool:
        """Switch the current model."""
        self.initialize()
        self._start_new_chat()
        success = self._switch_model(model, effort)
        if success:
            self._current_model = model
        return success
    
    def new_chat(self) -> None:
        """Start a fresh conversation."""
        self.initialize()
        self._start_new_chat()
        self._current_model = self.config["default_model"]
    
    def get_conversation_url(self) -> str:
        """Get the current conversation URL."""
        if self.page and not self.page.is_closed():
            return self.page.url
        return ""
    
    def close(self) -> None:
        """Close browser and cleanup."""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            self.logger.error(f"Error closing: {e}")
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            self._initialized = False
            self.logger.info("Browser closed")
    
    def __enter__(self):
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# ──────────────────────────────────────────────────────────────────────────────
# CLI / Standalone Usage
# ──────────────────────────────────────────────────────────────────────────────

def main():
    """Command-line interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ChatGPT Web Relay CLI")
    parser.add_argument("prompt", nargs="?", help="Prompt to send")
    parser.add_argument("-m", "--model", default="gpt-5.5-pro-extended", help="Model ID")
    parser.add_argument("-e", "--effort", default="high", help="Thinking effort")
    parser.add_argument("-i", "--image", help="Image file path")
    parser.add_argument("-f", "--file", help="File path")
    parser.add_argument("--deep-research", action="store_true", help="Use Deep Research")
    parser.add_argument("--new-chat", action="store_true", help="Start new chat")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--debug", action="store_true", help="Debug logging")
    
    args = parser.parse_args()
    
    if not args.prompt and not args.deep_research:
        parser.error("Prompt required unless using --deep-research")
    
    relay = ChatGPTWebRelay(config_path=args.config, debug=args.debug)
    
    try:
        if args.deep_research:
            result = relay.deep_research(args.prompt or "Research this topic")
        elif args.image:
            result = relay.ask_with_image(args.prompt, args.image, model=args.model, effort=args.effort)
        elif args.file:
            result = relay.ask_with_file(args.prompt, args.file, model=args.model, effort=args.effort)
        else:
            result = relay.ask(args.prompt, model=args.model, effort=args.effort, new_chat=args.new_chat)
        
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        
    finally:
        relay.close()


if __name__ == "__main__":
    main()