import asyncio
import datetime as dt

from datetime import datetime

from playwright.async_api import async_playwright
from utils.logger import get_logger

logger = get_logger(__name__)

class CliniciaClient:
    def __init__(self, email: str, password: str, base_url: str = "https://clinicia.com/app"):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.context = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        await self._login()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()

    async def _login(self):
        login_url = f"{self.base_url}/login.php"
        logger.info(f"Logging in to Clinicia at {login_url}")
        await self.page.goto(login_url)

        await self.page.fill('#username', self.email)
        await self.page.fill('#password', self.password)
        await self.page.click('button[type="submit"]')

        # await self.page.wait_for_load_state('networkidle', timeout=10000)
        logger.info("Successfully logged in to Clinicia")

    async def get_patients(self) -> list[dict]:
        await self.page.wait_for_selector("a[href='patient_list.php']", timeout=10000)
        patients_url = f"{self.base_url}/patient_list.php"
        logger.info(f"Fetching patients from {patients_url}")
        await self.page.goto(patients_url)
        await self.page.wait_for_selector("table#datatable tbody tr")

        rows = await self.page.query_selector_all("table#datatable tbody tr")
        patients = []

        for row in rows:
            cols = await row.query_selector_all("td")

            if len(cols) < 9:
                continue  # пропускаем неполные строки

            # Извлекаем текстовые значения
            sr_no = (await cols[0].inner_text()).strip()
            patient_id = (await cols[1].inner_text()).strip()

            # Имя + ссылка
            name_link_el = await cols[2].query_selector("a")
            if name_link_el:
                name = (await name_link_el.inner_text()).strip()
                link = await name_link_el.get_attribute("href")
            else:
                name = (await cols[2].inner_text()).strip()
                link = None

            age = (await cols[3].inner_text()).strip()
            gender = (await cols[4].inner_text()).strip()
            mobile = (await cols[5].inner_text()).strip()
            category = (await cols[6].inner_text()).strip()
            outstanding = (await cols[7].inner_text()).strip()
            date = (await cols[8].inner_text()).strip()

            patients.append({
                "sr_no": sr_no,
                "patient_id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "mobile": mobile,
                "category": category,
                "outstanding": outstanding,
                "date": date,
                "link": link,
            })

        return patients

    async def get_appointments(self, target_date: str = None) -> list[dict]:
        await self.page.wait_for_selector("a[href='calendar.php']", timeout=10000)
        appointments_url = f"{self.base_url}/calendar.php"
        logger.info(f"Fetching appointments from {appointments_url}")
        await self.page.goto(appointments_url)

        await self.page.wait_for_selector("button.fc-agendaDay-button")
        day_button = self.page.locator("button.fc-agendaDay-button")
        if await day_button.count() > 0:
            await day_button.first.click()
        await asyncio.sleep(1)
        await self.page.wait_for_selector("table", timeout=60000)

        if target_date is None:
            # target_date = datetime.today().date()
            target_date = (datetime.today().date() - dt.timedelta(days=1))
        while True:
            header_text = await self.page.locator(".fc-center h2").text_content()
            header_text = header_text.strip()
            try:
                current_date = datetime.strptime(header_text.strip(), "%B %d, %Y").date()
            except ValueError:
                current_date = datetime.strptime(header_text.strip(), "%b %d, %Y").date()

            if current_date == target_date:
                logger.info(f"Collect appointments for {target_date.strftime('%d.%m.%Y')}")
                appointments = await self.collect_appointments()

                logger.info(f"Received {len(appointments)} appointments")
                break
            elif current_date < target_date:
                await self.page.locator("button.fc-next-button").click()
                await self.page.wait_for_timeout(1000)
            else:
                await self.page.locator("button.fc-prev-button").click()
                await self.page.wait_for_timeout(1000)

        logger.info(f"Found {len(appointments)} appointments")
        return appointments

    async def collect_appointments(self):
        appointments = self.page.locator(".fc-event")
        count = await appointments.count()
        logger.info(f'Found {count} appointments')

        results = []

        for i in range(count):
            appointments = self.page.locator(".fc-event")
            await appointments.nth(i).click()
            await self.page.wait_for_timeout(500)

            modal = self.page.locator(".modal-content:visible").first
            await modal.wait_for(timeout=2000)

            data = {
                "date": await self.get_value(modal, "#app_date"),
                "department": await self.get_value(modal, "#clinic_list"),
                "patient_name": await self.get_value(modal, "#p_name"),
                "patient_phone": await self.get_value(modal, "#p_mobile_no"),
                "start_time": await self.get_value(modal, "#start_time"),
                "end_time": await self.get_value(modal, "#end_time"),
                "doctor": await self.get_value(modal, "#doc_list"),
                "remark": await self.get_value(modal, "#purpose_visit"),
                "status": await self.get_value(modal, "#status"),
            }
            results.append(data)

            try:
                await modal.locator("button.close").first.click()
                await self.page.wait_for_selector(".modal-content:visible", state="detached", timeout=5000)
            except Exception as e:
                logger.warning(f'Unexpected exception: {e}')
                await self.page.keyboard.press("Escape")

            await self.page.wait_for_timeout(500)

        return results

    @staticmethod
    async def get_value(modal, selector):
        el = modal.locator(selector)
        result = ''
        try:
            if await el.count() != 0:
                result = await el.input_value() or await el.text_content() or ""
        except Exception as e:
            logger.warning(f'Unexpected exception: {e}')
            result = await el.text_content() or ""
        return str(result).strip()


async def main():
    from utils.config import CLINICIA_EMAIL, CLINICIA_PASSWORD

    async with CliniciaClient(CLINICIA_EMAIL, CLINICIA_PASSWORD) as client:
        # patients = await client.get_patients()
        appointments = await client.get_appointments()

    # print(f"Patients: {len(patients)}")
    print(f"Appointments: {len(appointments)}")

    import json
    print(json.dumps(appointments, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
