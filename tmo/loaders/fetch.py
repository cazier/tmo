import contextlib
import csv
import dataclasses
import decimal
import logging
import os
import pathlib
import random
import re
import secrets
import time
import typing

import arrow
import playwright.async_api as playwright
import rich.logging

from .. import config
from ..lib import utilities
from ..web.routers.models.post import FillSubscriber, PostCharge, PostFilledBill

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(module)s:%(lineno)d - %(message)s",
    datefmt="[%X]",
    handlers=[rich.logging.RichHandler()],
)


def delayed[**P, T](func: typing.Callable[P, T]) -> typing.Callable[P, T]:
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        time.sleep(random.randint(1, 30) / 10)
        return func(*args, **kwargs)

    return inner


playwright.Locator.click = delayed(playwright.Locator.click)  # type: ignore[method-assign]


@dataclasses.dataclass
class Fetcher:
    user_agent: typing.Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = False
    login_domain: str = "https://tfb.t-mobile.com"

    report_id: str = dataclasses.field(init=False)
    account_number: str = dataclasses.field(init=False)

    page: playwright.Page = dataclasses.field(init=False)
    context: playwright.BrowserContext = dataclasses.field(init=False)
    browser: playwright.Browser = dataclasses.field(init=False)

    async def _launch(self, runner: playwright.Playwright, headless: bool | None = None) -> playwright.Browser:
        if headless is None:
            headless = self.headless

        browser: playwright.BrowserType = getattr(runner, self.user_agent)
        return await browser.launch(headless=headless)

    async def _get_user_agent(self) -> str | None:
        if not self.headless:
            return None

        async with playwright.async_playwright() as runner:
            browser = await self._launch(runner, True)
            context = await browser.new_context()
            page = await context.new_page()

            user_agent: str = await page.evaluate("navigator.userAgent")

            return user_agent.replace("Headless", "")

    @contextlib.asynccontextmanager
    async def session(self) -> typing.AsyncGenerator[None]:
        user_agent = await self._get_user_agent()

        async with playwright.async_playwright() as runner:
            self.browser = await self._launch(runner)
            self.context = await self.browser.new_context(user_agent=user_agent)
            self.page = await self.context.new_page()

            await self.context.tracing.start(screenshots=True, snapshots=True, sources=True)

            try:
                yield

            except BaseException as exc:
                await self.context.tracing.stop(path=pathlib.Path.cwd().joinpath(f"{secrets.token_hex(8)}.zip"))
                raise exc

            finally:
                for page in self.context.pages:
                    await page.close()

                await self.context.close()
                await self.browser.close()

    async def get_csv(self, date: arrow.Arrow) -> str:
        async with self.session():
            await self.login()
            await self.create_report(date)

            report = await self.download_report()

            await self.cleanup_report()

        return report

    async def login(self) -> None:
        logger.info("Starting login flow at %s", self.login_domain)

        logger.debug("Navigating to login page")
        await self.page.goto(self.login_domain)

        logger.info("Entering user ID in textbox")
        locator = self.page.get_by_role("textbox", name="Email or phone number", exact=True)
        await locator.press_sequentially(os.environ["TMO_FETCH_username"], delay=random.randint(100, 150))

        logger.debug("Submitting user ID data")
        await self.page.get_by_role("button", name="Next", exact=True).click()

        logger.info("Entering user password in textbox")
        locator = self.page.get_by_role("textbox", name="password")
        await locator.press_sequentially(os.environ["TMO_FETCH_password"], delay=random.randint(100, 150))

        logger.debug("Submitting user password")
        await self.page.get_by_role("button", name="Log in", exact=True).click()

        if os.getenv("TMO_FETCH_totp_secret"):
            await self.handle_totp()

        await playwright.expect(self.page.get_by_role("button", name="Manage Accounts", exact=True)).to_be_visible(
            timeout=15e3
        )

        await self.get_account_number()

    async def handle_totp(self) -> None:
        logger.info("Configuration includes a two-factor authentication method")
        await playwright.expect(
            self.page.get_by_role("heading", name="Let's confirm it's you", exact=True)
        ).to_be_visible()

        logger.debug("Redirected to the two-factor authentication page")
        box = await self.page.get_by_role("radio", name="Use Google Authenticator", exact=True).bounding_box()

        if not box:
            raise ValueError("Could not complete the TOTP process.")

        logger.info("Clicking on the Google Authenticator (TOTP) radio button")
        await self.page.mouse.click(box["x"] + (box["width"] / 2), box["y"] + (box["height"] / 2))

        logger.debug("Continuing to TOTP code entry")
        await self.page.get_by_role("button", name="Continue", exact=True).click()

        code = utilities.generate_totp(os.environ["TMO_FETCH_totp_secret"])
        logger.info("Entering TOTP code: %s", code)
        await self.page.get_by_role("textbox", name="code").press_sequentially(code, delay=random.randint(100, 150))

        logger.debug("Submitting TOTP code")
        await self.page.get_by_role("button", name="Continue", exact=True).click()

    async def get_account_number(self) -> None:
        logger.info("Trying to find an account number from the Dashboard page.")
        pattern = re.compile(r"Account #(\d+)")

        text = await self.page.get_by_text(pattern).text_content()

        if text and (groups := pattern.search(text)):
            self.account_number = groups.group(1)
            return

        raise ValueError("Could not find the account number from the dashboard page.")

    async def create_report(self, date: arrow.Arrow) -> None:
        self.report_id = secrets.token_hex(16)

        logger.info("Creating a new report named %s", self.report_id)

        logger.debug("Opening Reporting page")
        await self.page.get_by_role("button", name="Reporting", exact=True).click()

        logger.debug("Selecting reports tab")
        await self.page.get_by_role("tab", name="Reports", exact=True).click()

        logger.info("Generating report for %s %d", date.strftime("%B"), date.year)
        await self.page.get_by_role("combobox", name="Select", exact=True).click()
        await self.page.get_by_role("option", name=date.strftime("%B %Y"), exact=True).click()

        logger.info("Selecting node for account %s", self.account_number)
        await self.page.get_by_role("textbox", name="Node").click()
        await self.page.get_by_role("treeitem", name="951667996", exact=True).click()

        logger.debug("Customizing 'Charges and Usage Summary' report")
        row = self.page.get_by_role("button", name="Charges and Usage Summary Customize", exact=True)
        await row.get_by_text("Customize", exact=True).click()

        logger.debug("Setting report name to unique value")
        locator = self.page.get_by_role("textbox")

        logger.debug("Emptying initial report name and assigning random ID")
        await locator.fill("")
        await locator.press_sequentially(self.report_id, delay=random.randint(100, 150))

        logger.info("Initializing actual report creation")
        await self.page.get_by_role("button", name="Create Report", exact=True).click()

        await self.handle_modals()

    async def handle_modals(self) -> None:
        logger.info("Handling possible modal conflicts.")
        time.sleep(10)  # NOTE: This probably can be written to use a better expect tag?

        modal = self.page.get_by_role("dialog")
        text = await modal.text_content()

        if text is None:
            raise ValueError("Could not find a modal dialog with text contents")

        if "Your request was successfully processed." in text:
            logger.debug("The report was successfully processed, per the dialog box")
            await modal.get_by_role("button", name="Close", exact=True).click()

        elif "Report Creation in Progress" in text:
            logger.debug("The report is still processing, per the dialog box")
            await modal.get_by_role("button", name="Back", exact=True).click()

        else:
            raise Exception("Unknown modal type was found...")

        logger.debug("Returning to reports page")
        region = self.page.get_by_role("region", name="Reporting", exact=True)
        await region.get_by_text("My Reports", exact=True).click()

    async def _open_report_menu(self) -> None:
        logger.info("Opening the generated report %s", self.report_id)
        row = self.page.get_by_role("button", name=self.report_id)

        logger.debug("Opening the hamburger/elipsis icon for the report")
        await row.get_by_role("button").click()

    async def download_report(self) -> str:
        await self._open_report_menu()

        logger.debug("Opening download modal")
        await self.page.get_by_role("menuitem", name="Download", exact=True).click()

        async with self.page.expect_download() as event:
            logger.info("Finally getting the CSV file")
            await self.page.get_by_role("button", name="Download", exact=True).click()

        download = await event.value

        return (await download.path()).read_text(encoding="utf8")

    async def cleanup_report(self) -> None:
        await self._open_report_menu()

        logger.info("Deleting report from account")
        await self.page.get_by_role("menuitem", name="Delete", exact=True).click()


def _find_number(raw: str) -> tuple[str, str]:
    for number, name in config.load.numbers.items():
        if raw == number.replace("-", ""):
            return number, name

    return raw, "N/A"


def _ensure_zero(value: str) -> decimal.Decimal:
    amount = decimal.Decimal(value)

    if amount != decimal.Decimal("0"):
        raise ValueError("Need some more details for usage")

    return amount


def format_csv(data: str) -> PostFilledBill:
    # Removing special characters
    data = data.replace("$", "")

    header = ""

    taxes = decimal.Decimal("0")
    service = decimal.Decimal("0")

    for text in data.splitlines():
        if text.startswith("Billing Period Ending"):
            break

    bill = PostFilledBill(date=arrow.get(text, "MMMM YYYY").replace(day=1).shift(months=+1).date())

    for text in data.splitlines():
        if text.startswith("Subscriber"):
            header = text
            continue

        if header:
            [reader] = csv.DictReader([text], header.split(","))

            service += decimal.Decimal(reader["Plans"])
            taxes += decimal.Decimal(reader["Taxes and Fees"])

            number, name = _find_number(reader["Subscriber Number"])

            if name == "N/A":
                continue

            bill.subscribers.append(
                FillSubscriber.model_validate(
                    {
                        "name": name,
                        "number": number,
                        "minutes": reader["Talk Minutes"],
                        "messages": reader["Text Messages"],
                        "data": reader["Data "],
                        "phone": reader["Equipment"],
                        "line": 0,
                        "insurance": 0,
                        "usage": 0,
                    }
                )
            )

            for key in (
                "Usage Charges",
                "Services",
                "One-time Charges",
                "Immediate Charges",
                "Credits and Adjustments",
            ):
                _ensure_zero(reader[key])

    bill.charges.append(PostCharge(name="taxes", split=True, total=taxes))

    for subscriber in bill.subscribers:
        subscriber.line = service / len(bill.subscribers)

    bill.total = sum(
        (
            *(charge.total for charge in bill.charges),
            *(sub.phone + sub.line + sub.insurance + sub.usage for sub in bill.subscribers),
        ),
        start=decimal.Decimal(),
    )

    return bill
