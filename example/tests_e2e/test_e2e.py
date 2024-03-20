import os
import shutil
from django.apps import apps
from django.core.management import call_command
from playwright.sync_api import Page, expect

call_command("djelm", "compile", "elm_programs")
# remove parcel-cache
path = apps.get_app_config("elm_programs").path
shutil.rmtree(os.path.join(path, "static_src", ".parcel-cache"))


def test_addprogram(page: Page):
    """Renders a default elm program"""

    page.goto("localhost:8000/main")

    expect(page.get_by_role("button", name="+")).to_be_visible()


def test_addwidget(page: Page):
    """Renders a ModelChoiceField widget program"""

    page.goto("localhost:8000/promotion")

    expect(page.locator("data-test-id=selectContainer")).to_be_visible()


def test_modelChoiceField_form(page: Page):
    """Make a selection that validates on the server and persists the model"""

    page.goto("localhost:8000/promotion")
    page.locator("data-test-id=selectContainer").click()
    page.wait_for_selector("data-test-id=listBox")
    page.keyboard.press("ArrowDown")
    page.wait_for_selector("data-test-id=listBoxItemTargetFocus1")
    page.keyboard.press("Enter")
    page.wait_for_selector("data-test-id=selectedItem")
    page.get_by_role("button", name="Submit").click()
    page.wait_for_url("**/promotion_update/**")

    expect(page.get_by_text("Django Fundamentals")).to_be_visible()
