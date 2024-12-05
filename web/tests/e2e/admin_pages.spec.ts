import { test, expect } from "@playwright/test";
import { verifyAdminPageNavigation } from "./utils/adminSetup";
import testCases from "./testcases.json";

for (const testCase of testCases) {
  test(
    `Admin - ${testCase.name}`,
    {
      tag: "@admin",
    },
    async ({ page }) => {
      await verifyAdminPageNavigation(
        page,
        testCase.path,
        testCase.pageTitle,
        testCase.options
      );
    }
  );
}
