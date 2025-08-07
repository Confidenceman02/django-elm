import os
import shutil
from typing import Callable
from django.apps import apps
from django.core.management import call_command
from playwright.sync_api import ConsoleMessage, Page, expect
from unittest import TestCase

call_command("djelm", "compile", "elm_programs")
# remove parcel-cache
path = apps.get_app_config("elm_programs").path
shutil.rmtree(os.path.join(path, "static_src", ".parcel-cache"))


def assert_console_message(program_name: str) -> Callable[[ConsoleMessage], bool]:
    def check(msg: ConsoleMessage) -> bool:
        # Skip DEBUG messages
        if "DEBUG mode" in msg.text:
            return False
        TestCase().assertEqual(msg.type, "warning")
        TestCase().assertEqual(
            msg.text, f"'handleApp' Not implemented for '{program_name}'"
        )
        return True

    return check


def test_add_program_handlers(page: Page):
    """Test Main still compiles after adding handler"""
    call_command("djelm", "addprogramhandlers", "elm_programs", "Main")
    call_command("djelm", "compile", "elm_programs")

    page.goto("localhost:8000/main")

    page.expect_console_message(assert_console_message("Main.elm"))

    expect(page.get_by_role("button", name="+")).to_be_visible()


def test_add_widget_handlers(page: Page):
    """Test Widget still compiles after adding handler"""
    call_command(
        "djelm", "addprogramhandlers", "elm_programs", "Widgets.ModelChoiceField"
    )
    call_command("djelm", "compile", "elm_programs")

    page.goto("localhost:8000/promotion")
    page.expect_console_message(assert_console_message("ModelChoiceField.elm"))
    course = page.locator("#id_course")
    extras = page.locator("#id_extras")

    expect(course).to_be_visible()
    expect(extras).to_be_visible()


def test_addprogram(page: Page):
    """Renders a default elm program"""

    page.goto("localhost:8000/main")

    expect(page.get_by_role("button", name="+")).to_be_visible()


def test_addwidgets(page: Page):
    """Renders a ModelChoiceField and ModelMultipleChoiceField widget programs"""

    page.goto("localhost:8000/promotion")
    course = page.locator("#id_course")
    extras = page.locator("#id_extras")

    expect(course).to_be_visible()
    expect(extras).to_be_visible()


def test_promotion_form(page: Page):
    """Make a selection that validates on the server and persists the model"""

    page.goto("localhost:8000/promotion")
    course = page.locator("#id_course")
    extras = page.locator("#id_extras")

    # Course
    course.focus()
    page.keyboard.press("ArrowDown")
    page.wait_for_selector("data-test-id=listBox")
    page.keyboard.press("Enter")
    page.wait_for_selector("data-test-id=selectedItem")

    # Extras
    extras.focus()
    page.keyboard.press("ArrowDown")
    page.wait_for_selector("data-test-id=listBox")
    page.keyboard.press("Enter")
    page.wait_for_selector("data-test-id=multi-select-tag-0")

    # Submit
    page.get_by_role("button", name="Submit").click()
    page.wait_for_url("**/promotion_update/**")

    expect(page.get_by_text("Django Fundamentals")).to_be_visible()
