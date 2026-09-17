import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../..");
const fixtureRoot = path.join(repoRoot, "sample-data", "fixture-repository");

function zipFixture(): string {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "fixture-zip-"));
  const zipPath = path.join(outDir, "fixture-repository.zip");
  execFileSync("zip", ["-r", "-q", zipPath, "."], { cwd: fixtureRoot });
  return zipPath;
}

test("upload fixture zip, ask question, open cited excerpt", async ({
  page,
}) => {
  test.setTimeout(90_000);
  const zipPath = zipFixture();
  await page.goto("/");
  await expect(page.getByText("Codebase Assistant")).toBeVisible();

  await page.getByRole("button", { name: "Ingest a ZIP" }).click();
  await page.getByLabel("Repository ZIP").setInputFiles(zipPath);
  await page.getByRole("button", { name: "Ingest", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "New repository" })).toBeHidden({
    timeout: 60_000,
  });
  await expect(page.locator(".topbar-title")).toHaveText("fixture-repository");

  await page.getByRole("textbox", { name: "Message" }).fill(
    "Where is list_items defined?",
  );
  await page.getByRole("button", { name: "Send" }).click();

  const citation = page.locator(".citation-card").filter({
    has: page.locator(".citation-path[title='src/api/handlers.py']"),
  });
  await expect(citation).toBeVisible({ timeout: 60_000 });
  await citation.locator(".citation-card-header").click();
  await expect(
    page.getByRole("button", { name: "Copy source excerpt" }),
  ).toBeVisible();
  await expect(citation.locator(".excerpt-pre")).toContainText("list_items");

  await page.getByRole("textbox", { name: "Message" }).fill(
    "How does OAuth login work in this service?",
  );
  await page.getByRole("button", { name: "Send" }).click();
  await expect(page.getByText("Insufficient evidence")).toBeVisible({
    timeout: 60_000,
  });
});
