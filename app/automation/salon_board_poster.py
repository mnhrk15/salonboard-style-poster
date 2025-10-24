"""SALON BOARD style posting automation using Playwright."""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from app.core.config import settings

logger = logging.getLogger(__name__)


class SalonBoardStylePoster:
    """Automates style posting to SALON BOARD using Playwright.

    This class handles the entire automation workflow from login to posting
    multiple styles with images and metadata.
    """

    def __init__(
        self,
        selectors: dict[str, Any],
        screenshot_dir: str,
        headless: bool = True,
        slow_mo: int = 100,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        """Initialize the poster.

        Args:
            selectors: Selector configuration loaded from YAML.
            screenshot_dir: Directory to save error screenshots.
            headless: Whether to run browser in headless mode.
            slow_mo: Delay between operations in milliseconds.
            progress_callback: Optional callback function(completed, total) for progress
                updates. Should return False to interrupt the task.
        """
        self.selectors = selectors
        self.screenshot_dir = Path(screenshot_dir)
        self.headless = headless
        self.slow_mo = slow_mo
        self.check_and_report_progress_callback = progress_callback

        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

        # Ensure screenshot directory exists
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def _start_browser(self) -> None:
        """Start Playwright browser with anti-detection measures."""
        self.playwright = sync_playwright().start()

        # Launch Firefox with anti-detection settings
        self.browser = self.playwright.firefox.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

        # Create context with anti-detection measures
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
            viewport={"width": 1920, "height": 1080},
        )

        # Hide webdriver property
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.page = context.new_page()
        self.page.set_default_timeout(settings.PLAYWRIGHT_TIMEOUT)

        logger.info("Browser started successfully")

    def _close_browser(self) -> None:
        """Close browser and clean up resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed")

    def _take_screenshot(self, prefix: str = "error") -> str:
        """Take screenshot for debugging.

        Args:
            prefix: Prefix for screenshot filename.

        Returns:
            Path to saved screenshot.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.png"
        filepath = self.screenshot_dir / filename

        if self.page:
            self.page.screenshot(path=str(filepath))
            logger.info(f"Screenshot saved: {filepath}")

        return str(filepath)

    def _check_robot_detection(self) -> bool:
        """Check if robot detection (CAPTCHA, etc.) is present.

        Returns:
            True if robot detection detected, False otherwise.
        """
        if not self.page:
            return False

        # Check for selectors
        detection_selectors = self.selectors.get("robot_detection", {}).get("selectors", [])
        for selector in detection_selectors:
            if self.page.locator(selector).count() > 0:
                logger.error(f"Robot detection found: {selector}")
                return True

        # Check for texts
        detection_texts = self.selectors.get("robot_detection", {}).get("texts", [])
        for text in detection_texts:
            if self.page.locator(f"text={text}").count() > 0:
                logger.error(f"Robot detection text found: {text}")
                return True

        return False

    def _remove_widgets(self) -> None:
        """Remove interfering widgets (e.g., KARTE) from the page.

        This prevents widgets from blocking clicks or interfering with automation.
        Uses the widget selectors defined in selectors.yaml.
        """
        if not self.page:
            return

        widget_selectors = self.selectors.get("widget", {}).get("selectors", [])
        if not widget_selectors:
            return

        removed_count = 0
        for selector in widget_selectors:
            try:
                # Check if widget exists
                widget_count = self.page.locator(selector).count()
                if widget_count > 0:
                    # Remove all matching widgets from DOM
                    self.page.evaluate(f"""
                        () => {{
                            document.querySelectorAll('{selector}').forEach(el => el.remove());
                        }}
                    """)
                    removed_count += widget_count
                    logger.debug(f"Removed {widget_count} widget(s): {selector}")
            except Exception as e:
                logger.warning(f"Failed to remove widget {selector}: {e}")

        if removed_count > 0:
            logger.info(f"Removed {removed_count} widget(s) from page")

    def _click_and_wait(self, selector: str, timeout: int | None = None) -> None:
        """Click element and wait for navigation.

        Args:
            selector: CSS selector to click.
            timeout: Optional timeout in milliseconds.
        """
        if not self.page:
            raise RuntimeError("Page not initialized")

        self.page.locator(selector).first.click(timeout=timeout)
        self.page.wait_for_load_state("networkidle")

        # Remove interfering widgets after page load
        self._remove_widgets()

        if self._check_robot_detection():
            raise RuntimeError("Robot detection triggered")

    def step_login(self, user_id: str, password: str, salon_info: dict[str, str] | None = None) -> None:
        """Login to SALON BOARD and select salon if necessary.

        Args:
            user_id: SALON BOARD user ID.
            password: SALON BOARD password.
            salon_info: Optional salon selection info (id or name).

        Raises:
            RuntimeError: If login fails.
        """
        if not self.page:
            raise RuntimeError("Page not initialized")

        logger.info("Starting login process")

        # Navigate to login page
        login_url = self.selectors["login"]["url"]
        self.page.goto(login_url)

        if self._check_robot_detection():
            raise RuntimeError("Robot detection on login page")

        # Fill login form
        user_id_input = self.selectors["login"]["user_id_input"]
        password_input = self.selectors["login"]["password_input"]["primary"]
        login_button = self.selectors["login"]["login_button"]["primary"]

        self.page.locator(user_id_input).fill(user_id)
        self.page.locator(password_input).fill(password)

        self._click_and_wait(login_button)

        # Check if salon selection is needed (multi-store account)
        salon_list_table = self.selectors["salon_selection"]["salon_list_table"]
        if self.page.locator(salon_list_table).count() > 0:
            logger.info("Multi-store account detected, selecting salon")

            if not salon_info:
                raise RuntimeError("Salon selection required but no salon_info provided")

            # Get all salon rows
            salon_list_row = self.selectors["salon_selection"]["salon_list_row"]
            salon_name_cell = self.selectors["salon_selection"]["salon_name_cell"]
            salon_id_cell = self.selectors["salon_selection"]["salon_id_cell"]

            rows = self.page.locator(salon_list_row).all()

            for row in rows:
                row_salon_id = row.locator(salon_id_cell).text_content()
                row_salon_name = row.locator(salon_name_cell).text_content()

                # Match by ID or name
                if (salon_info.get("id") and row_salon_id == salon_info["id"]) or \
                   (salon_info.get("name") and row_salon_name == salon_info["name"]):
                    # Click the link in this row
                    row.locator("a").click()
                    self.page.wait_for_load_state("networkidle")
                    logger.info(f"Selected salon: {row_salon_name}")
                    break
            else:
                raise RuntimeError(f"Salon not found: {salon_info}")

        # Verify login success
        dashboard_navi = self.selectors["login"]["dashboard_global_navi"]
        self.page.wait_for_selector(dashboard_navi)
        logger.info("Login successful")

    def step_navigate_to_style_list_page(self) -> None:
        """Navigate to style management page.

        Raises:
            RuntimeError: If navigation fails.
        """
        if not self.page:
            raise RuntimeError("Page not initialized")

        logger.info("Navigating to style list page")

        # Click 掲載管理
        keisai_kanri = self.selectors["navigation"]["keisai_kanri"]
        self._click_and_wait(keisai_kanri)

        # Click スタイル管理
        style = self.selectors["navigation"]["style"]
        self._click_and_wait(style)

        logger.info("Navigated to style list page")

    def step_process_single_style(self, style_data: dict[str, Any], image_path: str) -> None:
        """Process and post a single style.

        Args:
            style_data: Dictionary containing style information.
            image_path: Path to style image file.

        Raises:
            RuntimeError: If posting fails.
        """
        if not self.page:
            raise RuntimeError("Page not initialized")

        logger.info(f"Processing style: {style_data.get('スタイル名', 'Unknown')}")

        # Click new style button
        new_style_button = self.selectors["style_form"]["new_style_button"]
        self._click_and_wait(new_style_button)

        # Upload image
        upload_area = self.selectors["style_form"]["image"]["upload_area"]
        modal_container = self.selectors["style_form"]["image"]["modal_container"]
        file_input = self.selectors["style_form"]["image"]["file_input"]
        submit_button = self.selectors["style_form"]["image"]["submit_button_active"]

        self.page.locator(upload_area).click()
        self.page.wait_for_selector(modal_container)
        self.page.locator(file_input).set_input_files(image_path)
        self.page.wait_for_selector(submit_button)
        self.page.locator(submit_button).click()
        self.page.wait_for_selector(modal_container, state="hidden")

        logger.info("Image uploaded")

        # Fill form fields
        if style_data.get("スタイリスト名"):
            stylist_select = self.selectors["style_form"]["stylist_name_select"]
            self.page.locator(stylist_select).select_option(label=style_data["スタイリスト名"])

        if style_data.get("コメント"):
            comment_textarea = self.selectors["style_form"]["stylist_comment_textarea"]
            self.page.locator(comment_textarea).fill(style_data["コメント"])

        if style_data.get("スタイル名"):
            style_name_input = self.selectors["style_form"]["style_name_input"]
            self.page.locator(style_name_input).fill(style_data["スタイル名"])

        # Category and length selection
        category = style_data.get("カテゴリ", "レディース").lower()
        if category == "レディース":
            category_radio = self.selectors["style_form"]["category_ladies_radio"]
            length_select = self.selectors["style_form"]["length_select_ladies"]
        else:
            category_radio = self.selectors["style_form"]["category_mens_radio"]
            length_select = self.selectors["style_form"]["length_select_mens"]

        self.page.locator(category_radio).click()

        if style_data.get("長さ"):
            self.page.locator(length_select).select_option(label=style_data["長さ"])

        if style_data.get("メニュー内容"):
            menu_detail = self.selectors["style_form"]["menu_detail_textarea"]
            self.page.locator(menu_detail).fill(style_data["メニュー内容"])

        # Select coupon if specified
        if style_data.get("クーポン名"):
            coupon_button = self.selectors["style_form"]["coupon"]["select_button"]
            coupon_modal = self.selectors["style_form"]["coupon"]["modal_container"]
            coupon_label_template = self.selectors["style_form"]["coupon"]["item_label_template"]
            coupon_setting = self.selectors["style_form"]["coupon"]["setting_button"]

            self.page.locator(coupon_button).click()
            self.page.wait_for_selector(coupon_modal)

            coupon_label = coupon_label_template.format(name=style_data["クーポン名"])
            self.page.locator(coupon_label).first.click()
            self.page.locator(coupon_setting).click()
            self.page.wait_for_selector(coupon_modal, state="hidden")

        # Add hashtags
        if style_data.get("ハッシュタグ"):
            hashtag_input = self.selectors["style_form"]["hashtag"]["input_area"]
            hashtag_button = self.selectors["style_form"]["hashtag"]["add_button"]

            hashtags = [tag.strip() for tag in style_data["ハッシュタグ"].split(",")]
            for tag in hashtags:
                if tag:
                    self.page.locator(hashtag_input).fill(tag)
                    self.page.locator(hashtag_button).click()
                    time.sleep(0.5)

        # Submit form
        register_button = self.selectors["style_form"]["register_button"]
        self._click_and_wait(register_button)

        # Wait for completion
        complete_text = self.selectors["style_form"]["complete_text"]
        self.page.wait_for_selector(complete_text)

        # Return to list
        back_button = self.selectors["style_form"]["back_to_list_button"]
        self._click_and_wait(back_button)

        logger.info(f"Style posted successfully: {style_data.get('スタイル名')}")

    def run(
        self,
        user_id: str,
        password: str,
        data_filepath: str,
        image_dir: str,
        salon_info: dict[str, str] | None = None,
        start_from_row: int = 0,
    ) -> dict[str, Any]:
        """Execute the entire automation workflow.

        Args:
            user_id: SALON BOARD user ID.
            password: SALON BOARD password.
            data_filepath: Path to CSV/Excel file with style data.
            image_dir: Directory containing image files.
            salon_info: Optional salon selection info.

        Returns:
            Dictionary with execution results.
        """
        results: dict[str, Any] = {
            "success": True,
            "total": 0,
            "completed": 0,
            "failed": 0,
            "errors": [],
        }

        try:
            # Start browser
            self._start_browser()

            # Login
            self.step_login(user_id, password, salon_info)

            # Load data file
            if data_filepath.endswith(".csv"):
                df = pd.read_csv(data_filepath)
            else:
                df = pd.read_excel(data_filepath)

            results["total"] = len(df)

            # Navigate to style list page (once)
            self.step_navigate_to_style_list_page()

            # Process each style, starting from the specified row
            for idx, row in df.iloc[start_from_row:].iterrows():
                # Check for interruption before processing the next item
                if self.check_and_report_progress_callback:
                    if not self.check_and_report_progress_callback(results["completed"], results["total"]):
                        logger.info("Task interrupted by external signal.")
                        break

                try:
                    style_data = row.to_dict()

                    # Get image path
                    image_filename = style_data.get("画像名")
                    if not image_filename:
                        raise ValueError("'画像名' column not specified in data")

                    image_path = Path(image_dir) / image_filename
                    if not image_path.exists():
                        raise FileNotFoundError(f"Image not found: {image_path}")

                    # Process style
                    self.step_process_single_style(style_data, str(image_path))

                    results["completed"] += 1

                except Exception as e:
                    logger.error(f"Failed to process style at row {idx}: {e}")
                    screenshot_path = self._take_screenshot(f"error_row_{idx}")

                    results["failed"] += 1
                    results["errors"].append({
                        "row": int(idx),
                        "style_name": style_data.get("スタイル名", "Unknown"),
                        "error": str(e),
                        "screenshot": screenshot_path,
                    })

                    # Continue with next style (don't break)
                    continue

            # Final progress update after loop finishes
            if self.check_and_report_progress_callback:
                self.check_and_report_progress_callback(results["completed"], results["total"])

        except Exception as e:
            logger.error(f"Critical error during automation: {e}")
            screenshot_path = self._take_screenshot("critical_error")

            results["success"] = False
            results["errors"].append({
                "error": str(e),
                "screenshot": screenshot_path,
            })

        finally:
            self._close_browser()

        return results


def load_selectors(selectors_path: str = "app/automation/selectors.yaml") -> dict[str, Any]:
    """Load selectors configuration from YAML file.

    Args:
        selectors_path: Path to selectors YAML file.

    Returns:
        Dictionary with selectors configuration.
    """
    with open(selectors_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
