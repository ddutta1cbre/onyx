import { test, expect } from "@playwright/test";

const screenSizes = [
  { width: 1920, height: 1080 },
  { width: 1366, height: 768 },
  { width: 360, height: 640 },
];

for (const size of screenSizes) {
  test(`test - ${size.width}x${size.height}`, async ({ page }) => {
    await page.setViewportSize(size);

    await page.goto("http://localhost:3000/chat");
    await page.screenshot({
      path: `screenshots/chat_page_${size.width}x${size.height}.png`,
    });
    await page.hover("body", { position: { x: 0, y: 100 } });
    await page.getByRole("link", { name: "Manage Assistants" }).click();
    await expect(page).toHaveURL("http://localhost:3000/assistants/mine");
    await page.screenshot({
      path: `screenshots/assistants_mine_page_${size.width}x${size.height}.png`,
    });

    await page.getByRole("button", { name: "Create New Assistant" }).click();
    await expect(page).toHaveURL("http://localhost:3000/assistants/new");
    await page.screenshot({
      path: `screenshots/create_assistant_page_${size.width}x${size.height}.png`,
    });
    await page.getByTestId("name").click();
    await page.getByTestId("name").fill("Test");
    await page.getByTestId("description").click();
    await page.getByTestId("description").fill("Test");
    await page.getByTestId("system_prompt").click();
    await page.getByTestId("system_prompt").fill("Test");
    await page
      .getByRole("button", { name: "Logo GPT 4o", exact: true })
      .click();
    await page.getByRole("button", { name: "Create!" }).click();
    await page.waitForURL("http://localhost:3000/chat");
    await expect(page).toHaveURL("http://localhost:3000/chat");
    await page.screenshot({
      path: `screenshots/chat_page_after_create_${size.width}x${size.height}.png`,
    });
    await page.getByPlaceholder("Send a message or try using").fill("Hello");
    await expect(page.locator("#danswer-ai-message")).toBeVisible();
  });
}
