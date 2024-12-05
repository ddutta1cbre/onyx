import { test, expect } from "@playwright/test";

test("test", async ({ page }) => {
  await page.goto("http://localhost:3000/chat");
  await page.hover("body", { position: { x: 0, y: 100 } });
  await page.getByRole("link", { name: "Manage Assistants" }).click();
  await expect(page).toHaveURL("http://localhost:3000/assistants/mine");
  await page.getByRole("button", { name: "Create New Assistant" }).click();
  await expect(page).toHaveURL("http://localhost:3000/assistants/new");
  await page.getByTestId("name").click();
  await page.getByTestId("name").fill("Test");
  await page.getByTestId("description").click();
  await page.getByTestId("description").fill("Test");
  await page.getByTestId("system_prompt").click();
  await page.getByTestId("system_prompt").fill("Test");
  await page.getByRole("button", { name: "Logo GPT 4o", exact: true }).click();
  await page.getByRole("button", { name: "Create!" }).click();
  await page.waitForURL("http://localhost:3000/chat");
  await expect(page).toHaveURL("http://localhost:3000/chat");
  await page.getByPlaceholder("Send a message or try using").click();
  await page.getByPlaceholder("Send a message or try using").fill("Hello");
  await expect(page.locator("#danswer-ai-message")).toBeVisible();
  await page.locator("#danswer-human-message").click();
});
