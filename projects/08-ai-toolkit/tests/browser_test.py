"""Browser regression test for the Streamlit UI using Playwright."""
import asyncio
import os

from playwright.async_api import async_playwright, expect


APP_URL = os.getenv("APP_URL", "http://localhost:8501")
HEADLESS = os.getenv("HEADLESS", "1") != "0"


async def wait_for_body_text(page, needle: str, timeout_ms: int = 10000) -> str:
    """Wait until the page body contains a string and return the body text."""
    deadline = timeout_ms // 500
    for _ in range(deadline):
        body = await page.locator("body").inner_text()
        if needle in body:
            return body
        await page.wait_for_timeout(500)
    raise AssertionError(f"missing text: {needle!r}")


async def assert_spinner(page, needle: str) -> None:
    """Assert that a spinner message is visible before the result resolves."""
    await expect(page.get_by_text(needle)).to_be_visible(timeout=3000)


async def open_expander(page, label: str) -> None:
    """Open a Streamlit expander by its visible label."""
    expander = page.locator("[data-testid='stExpander']").filter(has_text=label).first
    await expander.click()
    await page.wait_for_timeout(500)


async def run_browser_tests() -> bool:
    """Run the browser regression flow against the Streamlit app."""
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page(viewport={"width": 1400, "height": 1200})

        print(f"Navigating to {APP_URL}...")
        await page.goto(APP_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector(".stApp", timeout=30000)
        print(f"Page loaded: {await page.title()}")

        print("\n=== Testing Interactive Mode ===\n")

        print("1. Testing interactive search...")
        try:
            await page.locator("textarea").first.fill("Search docs for Python")
            await page.get_by_role("button", name="Run").first.click()
            await assert_spinner(page, "Processing...")
            body = await wait_for_body_text(page, "Detected tool: search_docs")
            assert "Introduction to Python" in body
            results.append(("interactive_search", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("interactive_search", "FAIL"))
            print(f"   FAIL: {e}")

        print("2. Testing interactive Chuck Norris...")
        try:
            await page.locator("textarea").first.fill("Tell me a Chuck Norris fact")
            await page.get_by_role("button", name="Run").first.click()
            await assert_spinner(page, "Processing...")
            body = await wait_for_body_text(page, "Detected tool: get_chuck_norris_fact")
            assert "fact" in body.lower()
            results.append(("interactive_chuck_norris", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("interactive_chuck_norris", "FAIL"))
            print(f"   FAIL: {e}")

        print("\n=== Testing Tool Explorer Mode ===\n")

        try:
            await page.locator("label").filter(has_text="Tool Explorer").click()
            await page.wait_for_timeout(1000)
        except Exception:
            # If the radio label is already selected, keep going.
            pass

        print("2b. Testing interactive no-tool state...")
        try:
            await page.locator("textarea").first.fill("Hello there")
            await page.get_by_role("button", name="Run").first.click()
            body = await wait_for_body_text(page, "No tool detected")
            results.append(("interactive_no_tool", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("interactive_no_tool", "FAIL"))
            print(f"   FAIL: {e}")

        print("3. Testing search_docs...")
        try:
            await open_expander(page, "Search Documentation")
            await page.get_by_label("Search query:").fill("Python")
            await page.get_by_role("button", name="Run Search Documentation").click()
            await assert_spinner(page, "Running Search Documentation...")
            body = await wait_for_body_text(page, "Introduction to Python")
            assert '"query":"Python"' in body.replace(" ", "")
            results.append(("search_docs", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("search_docs", "FAIL"))
            print(f"   FAIL: {e}")

        print("4. Testing read_document...")
        try:
            await open_expander(page, "Read Document")
            await page.get_by_label("Document ID:").nth(0).fill("123")
            await page.get_by_role("button", name="Run Read Document").click()
            await assert_spinner(page, "Running Read Document...")
            body = await wait_for_body_text(page, "Document 123")
            assert '"id":"123"' in body.replace(" ", "")
            results.append(("read_document", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("read_document", "FAIL"))
            print(f"   FAIL: {e}")

        print("5. Testing summarise_document...")
        try:
            await open_expander(page, "Summarise Document")
            await page.get_by_label("Document ID:").nth(1).fill("456")
            await page.get_by_role("button", name="Run Summarise Document").click()
            await assert_spinner(page, "Running Summarise Document...")
            body = await wait_for_body_text(page, "Summary of Document 456")
            assert '"id":"456"' in body.replace(" ", "")
            results.append(("summarise_document", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("summarise_document", "FAIL"))
            print(f"   FAIL: {e}")

        print("6. Testing extract_keywords...")
        try:
            await open_expander(page, "Extract Keywords")
            await page.get_by_role("textbox", name="Text:").first.fill(
                "Machine learning and deep learning are popular topics."
            )
            await page.get_by_role("button", name="Run Extract Keywords").click()
            await assert_spinner(page, "Running Extract Keywords...")
            body = await wait_for_body_text(page, "keyword1")
            assert '"count":3' in body.replace(" ", "")
            results.append(("extract_keywords", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("extract_keywords", "FAIL"))
            print(f"   FAIL: {e}")

        print("7. Testing answer_question...")
        try:
            await open_expander(page, "Answer Question")
            await page.get_by_label("Question:").fill("What is Python?")
            await page.get_by_label("Context:").fill("Python is a programming language.")
            await page.get_by_role("button", name="Run Answer Question").click()
            await assert_spinner(page, "Running Answer Question...")
            body = await wait_for_body_text(page, "What is Python?")
            assert "programming language" in body
            results.append(("answer_question", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("answer_question", "FAIL"))
            print(f"   FAIL: {e}")

        print("8. Testing get_chuck_norris_fact...")
        try:
            await open_expander(page, "Chuck Norris Fact")
            await page.get_by_role("button", name="Run Chuck Norris Fact").click()
            await assert_spinner(page, "Running Chuck Norris Fact...")
            body = await wait_for_body_text(page, "fact")
            assert "url" in body.lower()
            results.append(("get_chuck_norris_fact", "PASS"))
            print("   PASS")
        except Exception as e:
            results.append(("get_chuck_norris_fact", "FAIL"))
            print(f"   FAIL: {e}")

        await browser.close()

    print("\n=== Summary ===")
    passed = sum(1 for _, result in results if result == "PASS")
    for name, result in results:
        print(f"  {name}: {result}")
    print(f"\nTotal: {passed}/{len(results)} tests passed")

    return passed == len(results)


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(run_browser_tests()) else 1)
